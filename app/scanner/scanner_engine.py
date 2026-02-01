# app/scanner/scanner_engine.py

from typing import List, Dict, Any, Tuple

from app.data.loaders import load_market_data
from app.features.technicals import add_technicals
from app.signals.signal_engine import SignalEngine
from app.scanner.universe import get_usdt_universe


# ------------------------------------------------------------
# PREFILTRO: reduce universo a TOP 50 (rápido y seguro)
# ------------------------------------------------------------
def prefilter_universe(symbols, timeframe: str = "1h", limit: int = 50) -> List[str]:
    # ✅ Blindaje: limit SIEMPRE int
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 50

    if limit <= 0:
        limit = 50

    scored: List[Tuple[str, float]] = []

    for symbol in symbols:
        try:
            df = load_market_data(symbol, timeframe, 100)
            if df is None or df.empty:
                continue

            # Métricas simples y robustas
            vol = float(df["volume"].iloc[-1])
            volat = float((df["high"] - df["low"]).mean())

            score = vol * volat
            scored.append((symbol, score))

        except Exception:
            continue

    scored.sort(key=lambda x: x[1], reverse=True)

    # ✅ Retorna TOP N símbolos
    return [s for s, _ in scored[:limit]]


# ------------------------------------------------------------
# SCANNER PRINCIPAL
# ------------------------------------------------------------
def scan_market(timeframe: str = "1h", limit: int = 300) -> List[Dict[str, Any]]:
    """
    Escanea el universo USDT Binance:
    - Prefiltra TOP 50
    - Analiza profundo
    - Devuelve TOP 5 señales BUY o SELL ordenadas por probabilidad
    """

    # ✅ Normalización extra: evita timeframe duplicado "1h1h"
    timeframe = (timeframe or "1h").strip()
    if len(timeframe) % 2 == 0 and timeframe[: len(timeframe) // 2] == timeframe[len(timeframe) // 2 :]:
        timeframe = timeframe[: len(timeframe) // 2]

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 300

    if limit <= 0:
        limit = 300

    engine = SignalEngine()
    results: List[Dict[str, Any]] = []

    # 1) Universo completo
    all_symbols = get_usdt_universe()

    # 2) Prefiltro institucional (TOP 50)
    symbols = prefilter_universe(all_symbols, timeframe=timeframe, limit=50)

    for symbol in symbols:
        try:
            df = load_market_data(symbol, timeframe, limit)
            if df is None or df.empty:
                continue

            df = add_technicals(df)

            signal = engine.generate(df)

            # ✅ BLINDAJE TOTAL
            if not isinstance(signal, dict):
                continue

            # ✅ aceptar BUY o SELL
            sig = signal.get("signal")
            if sig not in ("BUY", "SELL"):
                continue

            prob = signal.get("probability", 0.0)
            try:
                prob = float(prob)
            except Exception:
                prob = 0.0

            entry = signal.get("entry")
            stop = signal.get("stop")
            take_profit = signal.get("take_profit")

            results.append(
                {
                    "symbol": symbol,
                    "signal": sig,  # ✅ BUY o SELL real
                    "probability": prob,
                    "entry": float(entry) if entry is not None else None,
                    "stop": float(stop) if stop is not None else None,
                    "take_profit": float(take_profit) if take_profit is not None else None,
                    "regime": signal.get("regime"),
                    "reason": signal.get("reason"),
                }
            )

        except Exception:
            # Error aislado por símbolo (NO rompe todo)
            continue

    # 3) Ordenar por probabilidad
    results = sorted(results, key=lambda x: x.get("probability", 0.0), reverse=True)

    # 4) Devolver SOLO TOP 5
    return results[:5]


