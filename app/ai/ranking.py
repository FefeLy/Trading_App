# app/ai/ranking.py

from __future__ import annotations
from typing import Any, Dict, Tuple

import pandas as pd


def _safe_int(x: Any, default: int) -> int:
    try:
        v = int(x)
    except (TypeError, ValueError):
        return default
    return v if v > 0 else default


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return float(default)
        return float(x)
    except (TypeError, ValueError):
        return float(default)


def _has_cols(df: pd.DataFrame, cols: Tuple[str, ...]) -> bool:
    return df is not None and not df.empty and all(c in df.columns for c in cols)


def rank_signals(df: pd.DataFrame, regime: str = "neutral") -> float:
    """
    rank_signals(df, regime) -> float

    Devuelve un SCORE numérico para ordenar candidatos en scanner.py:
      ranked = sorted(candidates, key=lambda x: x["score"], reverse=True)[:top_n]

    Requisitos:
    - Nunca debe tirar excepción (el scanner debe seguir corriendo)
    - Nunca debe devolver dict/string (solo número)
    - Debe funcionar con tus DataFrames de Binance (open/high/low/close/volume)
    """

    try:
        # Validación rápida
        if df is None or df.empty:
            return 0.0

        # Requiere estas columnas mínimas
        if not _has_cols(df, ("close", "high", "low", "volume")):
            return 0.0

        # Asegurar tipo numérico y eliminar NaN/inf
        close = pd.to_numeric(df["close"], errors="coerce")
        high = pd.to_numeric(df["high"], errors="coerce")
        low = pd.to_numeric(df["low"], errors="coerce")
        volume = pd.to_numeric(df["volume"], errors="coerce")

        # Eliminar valores rotos
        close = close.dropna()
        high = high.dropna()
        low = low.dropna()
        volume = volume.dropna()

        if len(close) < 30:
            return 0.0

        # Ventanas seguras (int sí o sí)
        w_fast = _safe_int(14, 14)
        w_slow = _safe_int(28, 28)
        w_ret = _safe_int(12, 12)

        # Si el DF es pequeño, baja ventanas
        n = int(len(close))
        if n < w_slow + 2:
            w_slow = max(10, n // 2)
            w_fast = max(5, w_slow // 2)
            w_ret = max(5, w_fast)

        # =========================
        # 1) Momentum / Retorno
        # =========================
        last = _safe_float(close.iloc[-1], 0.0)
        prev = _safe_float(close.iloc[-w_ret], 0.0)

        if last <= 0.0 or prev <= 0.0:
            ret_score = 0.0
        else:
            ret_score = (last / prev) - 1.0  # retorno relativo

        # =========================
        # 2) Tendencia simple (EMA)
        # =========================
        ema_fast = close.ewm(span=w_fast, adjust=False).mean()
        ema_slow = close.ewm(span=w_slow, adjust=False).mean()

        trend = _safe_float(ema_fast.iloc[-1] - ema_slow.iloc[-1], 0.0)

        # Normalizar trend respecto al precio
        if last > 0:
            trend_score = trend / last
        else:
            trend_score = 0.0

        # =========================
        # 3) Volatilidad (rango)
        # =========================
        # volatilidad aproximada: promedio de (high-low)/close
        hl = (high - low).abs()

        # alineación por índice (por si dropna cambió tamaño)
        min_len = min(len(close), len(hl))
        if min_len < 10:
            vol_score = 0.0
        else:
            close2 = close.iloc[-min_len:]
            hl2 = hl.iloc[-min_len:]
            denom = close2.replace(0, pd.NA).dropna()

            if denom.empty:
                vol_score = 0.0
            else:
                rng = (hl2.iloc[-10:].mean() / close2.iloc[-10:].mean()) if close2.iloc[-10:].mean() != 0 else 0.0
                vol_score = _safe_float(rng, 0.0)

        # =========================
        # 4) Liquidez / Volumen
        # =========================
        # volumen relativo: último volumen / promedio 20 velas
        if len(volume) < 25:
            volu_score = 0.0
        else:
            last_vol = _safe_float(volume.iloc[-1], 0.0)
            avg_vol = _safe_float(volume.iloc[-20:].mean(), 0.0)

            if avg_vol <= 0:
                volu_score = 0.0
            else:
                volu_score = (last_vol / avg_vol)

        # =========================
        # Score final (robusto)
        # =========================
        # Retorno y tendencia = lo principal
        # Volatilidad y volumen modulan el ranking

        # Limitar extremos para evitar locuras por datos raros
        ret_score = max(min(ret_score, 0.20), -0.20)        # -20% a +20%
        trend_score = max(min(trend_score, 0.05), -0.05)    # -5% a +5%
        vol_score = max(min(vol_score, 0.20), 0.0)          # 0 a 20%
        volu_score = max(min(volu_score, 10.0), 0.0)        # 0 a 10x

        # Normalización ligera del volumen para que no domine
        volu_norm = min(volu_score / 3.0, 3.0)  # 0..3

        base = (ret_score * 0.60) + (trend_score * 0.40)

        # Penaliza si volatilidad está MUY baja (no se mueve) o MUY alta (ruidoso)
        # Esto es suave para no matar señales
        if vol_score < 0.005:
            base *= 0.85
        elif vol_score > 0.12:
            base *= 0.90

        # Ajuste por volumen (solo empuja un poco)
        base *= (1.0 + (volu_norm * 0.05))  # +0% a +15%

        # Ajuste por régimen
        r = (regime or "").lower().strip()

        if r == "bull":
            base *= 1.08
        elif r == "bear":
            base *= 0.85
        else:
            base *= 1.0

        # Nunca devuelvas NaN
        score = _safe_float(base, 0.0)

        # Si algo quedó raro, neutraliza
        if score != score:  # NaN check
            return 0.0

        return float(score)

    except Exception:
        # Blindaje total: nunca romper scanner
        return 0.0
