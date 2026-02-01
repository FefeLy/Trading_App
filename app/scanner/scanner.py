import time
from typing import List, Dict, Any

from app.data.binance_client import load_market_data, get_top_usdt_pairs_by_volume
from app.features.technicals import add_technicals
from app.ai.regime import detect_market_regime
from app.signals.signal_engine import generate_signal


def _safe_float(x, default=0.0) -> float:
    try:
        if x is None:
            return float(default)
        return float(x)
    except Exception:
        return float(default)


def _normalize_regime(regime_raw) -> str:
    """
    Normaliza el régimen a: bull / bear / neutral
    """
    try:
        r = regime_raw.value if hasattr(regime_raw, "value") else str(regime_raw)
        r = str(r).lower().strip()
    except Exception:
        return "neutral"

    if r in ("trending", "trend", "uptrend", "bull", "bullish"):
        return "bull"
    if r in ("downtrend", "bear", "bearish"):
        return "bear"
    if r in ("range", "ranging", "sideways", "neutral", "flat"):
        return "neutral"

    return "neutral"


def _classify_strength(prob: float) -> str:
    """
    Swing = más exigente, pero no imposible.
    """
    if prob >= 0.80:
        return "STRONG"
    if prob >= 0.70:
        return "WEAK"
    return "NONE"


def scan_universe_swing(
    timeframe_entry: str = "1h",
    timeframe_direction: str = "4h",
    timeframe_macro: str = "1d",
    universe_size: int = 50,
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Scanner institucional SWING:
    - 1D = macro filtro
    - 4H = dirección
    - 1H = entrada y ejecución
    """

    t0 = time.time()

    symbols = get_top_usdt_pairs_by_volume(top_n=int(universe_size))

    telemetry: Dict[str, Any] = {
        "symbols_loaded": len(symbols),
        "empty_data": 0,
        "exceptions": 0,
        "actionable": 0,
        "elapsed_ms": 0,

        # 👇 debug institucional
        "regimes": {"bull": 0, "bear": 0, "neutral": 0},
        "filtered": {
            "neutral_dir": 0,
            "macro_conflict": 0,
            "hold_or_none": 0,
            "low_prob": 0,
        },
        "errors": [],
    }

    candidates: List[Dict[str, Any]] = []

    for symbol in symbols:
        try:
            # ==========================
            # 1) Cargar multi-timeframe
            # ==========================
            df_entry = load_market_data(symbol=symbol, timeframe=timeframe_entry, limit=260)
            df_dir = load_market_data(symbol=symbol, timeframe=timeframe_direction, limit=260)
            df_mac = load_market_data(symbol=symbol, timeframe=timeframe_macro, limit=220)

            if df_entry is None or getattr(df_entry, "empty", True):
                telemetry["empty_data"] += 1
                continue
            if df_dir is None or getattr(df_dir, "empty", True):
                telemetry["empty_data"] += 1
                continue
            if df_mac is None or getattr(df_mac, "empty", True):
                telemetry["empty_data"] += 1
                continue

            # ==========================
            # 2) Técnicos PRO
            # ==========================
            df_entry = add_technicals(df_entry)
            df_dir = add_technicals(df_dir)
            df_mac = add_technicals(df_mac)

            if df_entry is None or getattr(df_entry, "empty", True):
                telemetry["empty_data"] += 1
                continue

            # ==========================
            # 3) Regímenes (macro + dirección)
            # ==========================
            regime_dir = _normalize_regime(detect_market_regime(df_dir))
            regime_mac = _normalize_regime(detect_market_regime(df_mac))

            telemetry["regimes"][regime_dir] = telemetry["regimes"].get(regime_dir, 0) + 1

            # ✅ Swing institucional: evitar neutral en 4H
            if regime_dir == "neutral":
                telemetry["filtered"]["neutral_dir"] += 1
                continue

            # ✅ Macro filtro: evitar ir contra 1D FUERTE
            # (OJO: no bloqueamos neutral macro, solo conflicto real)
            if (regime_dir == "bull" and regime_mac == "bear") or (regime_dir == "bear" and regime_mac == "bull"):
                telemetry["filtered"]["macro_conflict"] += 1
                continue

            # ==========================
            # 4) Threshold swing (estricto pero realista)
            # ==========================
            base_threshold = 0.60

            # si macro es neutral, subir requisito un poco (mercado indeciso)
            if regime_mac == "neutral":
                base_threshold += 0.02

            # ==========================
            # 5) Generar señal (ENTRY timeframe)
            # ==========================
            sig = generate_signal(df=df_entry, threshold=base_threshold)

            signal = str(sig.get("signal", "HOLD")).upper()
            entry = sig.get("entry", None)
            stop = sig.get("stop", None)
            take_profit = sig.get("take_profit", None)

            prob = sig.get("probability", sig.get("confidence", sig.get("score", 0.0)))
            prob = _safe_float(prob, 0.0)

            strength = _classify_strength(prob)

            # ✅ Coherencia con 4H (dirección manda)
            if regime_dir == "bull" and signal == "SELL":
                signal = "HOLD"
            if regime_dir == "bear" and signal == "BUY":
                signal = "HOLD"

            # ✅ FILTRO FINAL institucional (pero NO exagerado)
            if signal == "HOLD":
                telemetry["filtered"]["hold_or_none"] += 1

                # ✅ DEBUG PRO: guardar candidatos HOLD con score bajo
                # (solo para UI / monitoreo, NO para operar)
                item = {
                    "symbol": symbol,
                    "signal": "HOLD",
                    "strength": "NONE",
                    "entry": sig.get("entry", None),
                    "stop": sig.get("stop", None),
                    "take_profit": sig.get("take_profit", None),
                    "probability": round(prob, 6),
                    "score": round(float(prob), 6),
                    "regime_4h": regime_dir,
                    "regime_1d": regime_mac,
                    "timeframe_entry": timeframe_entry,
                    "debug_only": True,
                }
                candidates.append(item)
                continue


            # prob mínima para swing real
            if prob < 0.70:
                telemetry["filtered"]["low_prob"] += 1
                continue

            if strength == "NONE":
                telemetry["filtered"]["hold_or_none"] += 1
                continue

            # ==========================
            # 6) Score institucional (ranking)
            # ==========================
            score = float(prob)

            # premio si macro y dirección alineadas
            if regime_mac == regime_dir:
                score += 0.03

            item = {
                "symbol": symbol,
                "signal": signal,
                "strength": strength,
                "entry": entry,
                "stop": stop,
                "take_profit": take_profit,
                "probability": round(prob, 6),
                "score": round(score, 6),
                "regime_4h": regime_dir,
                "regime_1d": regime_mac,
                "timeframe_entry": timeframe_entry,
            }

            candidates.append(item)

        except Exception as e:
            telemetry["exceptions"] += 1
            telemetry["errors"].append({"symbol": symbol, "error": str(e)})
            continue

    # ==========================
    # Ranking final
    # ==========================
    candidates = sorted(candidates, key=lambda x: x.get("score", 0.0), reverse=True)
    results = candidates[: max(1, int(top_n))] if candidates else []

    if results:
        telemetry["actionable"] = 1
        primary = results[0]
    else:
        primary = {
            "symbol": None,
            "signal": "HOLD",
            "strength": "NONE",
            "reason": "no_actionable_candidates",
            "timeframe_entry": timeframe_entry,
        }

    telemetry["elapsed_ms"] = int((time.time() - t0) * 1000)

    return {
        "status": "ok",
        "mode": "SWING_INSTITUTIONAL",
        "universe_size": int(universe_size),
        "returned": len(results),
        "primary_signal": primary,
        "results": results,
        "telemetry": telemetry,
    }


def run_market_scan(timeframe: str = "1h", universe_size: int = 50, top_n: int = 5) -> Dict[str, Any]:
    """
    Wrapper compatibilidad:
    Tu API vieja importa run_market_scan
    y aquí conectamos al scanner institucional swing.
    """
    return scan_universe_swing(
        timeframe_entry=str(timeframe),
        timeframe_direction="4h",
        timeframe_macro="1d",
        universe_size=int(universe_size),
        top_n=int(top_n),
    )
