import pandas as pd
import numpy as np


def add_technicals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Technicals PRO / Institucional:
    - EMAs (20/50/12/26)
    - RSI (14)
    - ATR (14)
    - Volatility (20)
    - MACD (12,26,9)
    - ADX (14)
    - VWAP
    - Bollinger Bands (20,2)
    - Volume filters
    """

    # ✅ BLINDAJE CRÍTICO
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    if df.empty:
        return df

    required_cols = {"open", "high", "low", "close", "volume"}
    if not required_cols.issubset(df.columns):
        return pd.DataFrame()

    df = df.copy()

    # ============================
    # ✅ EMAs
    # ============================
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()

    # ✅ Alias para compatibilidad con SignalEngine
    df["ema20"] = df["ema_20"]
    df["ema50"] = df["ema_50"]

    # ============================
    # ✅ RSI (14)
    # ============================
    delta = df["close"].diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / (avg_loss.replace(0, np.nan))
    df["rsi"] = 100 - (100 / (1 + rs))
    df["rsi"] = df["rsi"].fillna(50.0)

    # ============================
    # ✅ ATR (14)
    # ============================
    high_low = (df["high"] - df["low"]).abs()
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()

    # ============================
    # ✅ Volatility (20)
    # ============================
    df["return"] = df["close"].pct_change()
    df["volatility"] = df["return"].rolling(20).std()

    # ============================
    # ✅ MACD (12,26,9)
    # ============================
    macd_line = df["ema_fast"] - df["ema_slow"]
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_signal

    df["macd"] = macd_line
    df["macd_signal"] = macd_signal
    df["macd_hist"] = macd_hist

    # Cruces MACD
    df["macd_cross_up"] = (df["macd"].shift(1) <= df["macd_signal"].shift(1)) & (df["macd"] > df["macd_signal"])
    df["macd_cross_down"] = (df["macd"].shift(1) >= df["macd_signal"].shift(1)) & (df["macd"] < df["macd_signal"])

    # ============================
    # ✅ ADX (14) - Fuerza de tendencia institucional
    # ============================
    # +DM / -DM
    up_move = df["high"].diff()
    down_move = -df["low"].diff()

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # TR ya calculado arriba
    atr = tr.rolling(14).mean()

    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(14).sum() / (atr.replace(0, np.nan)))
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(14).sum() / (atr.replace(0, np.nan)))

    dx = (100 * (plus_di - minus_di).abs() / ((plus_di + minus_di).replace(0, np.nan)))
    df["adx"] = dx.rolling(14).mean()

    df["plus_di"] = plus_di.fillna(0.0)
    df["minus_di"] = minus_di.fillna(0.0)
    df["adx"] = df["adx"].fillna(0.0)

    # ============================
    # ✅ VWAP (proxy) - institucional
    # ============================
    # VWAP real requiere "typical price * volume" acumulado intradía.
    # Aquí hacemos proxy rolling para timeframe general.
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = typical_price * df["volume"]
    df["vwap"] = (pv.rolling(20).sum() / df["volume"].rolling(20).sum()).replace([np.inf, -np.inf], np.nan)

    # ============================
    # ✅ Bollinger Bands (20,2)
    # ============================
    ma20 = df["close"].rolling(20).mean()
    std20 = df["close"].rolling(20).std()
    df["bb_mid"] = ma20
    df["bb_up"] = ma20 + (2.0 * std20)
    df["bb_low"] = ma20 - (2.0 * std20)

    # ============================
    # ✅ Volume filters institucional
    # ============================
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / (df["vol_ma20"].replace(0, np.nan))

    # ============================
    # ✅ Trend flags (para el SignalEngine)
    # ============================
    df["trend_bull"] = (df["close"] > df["ema_50"]) & (df["ema_20"] > df["ema_50"])
    df["trend_bear"] = (df["close"] < df["ema_50"]) & (df["ema_20"] < df["ema_50"])

    # ============================
    # ✅ Limpieza final
    # ============================
    df = df.replace([np.inf, -np.inf], np.nan)

    return df
