from typing import List
import time
import pandas as pd
from binance.client import Client

# ==========================
# CACHE USDT UNIVERSE
# ==========================
_USDT_CACHE: List[str] = []
_USDT_CACHE_TS: float = 0.0
_USDT_CACHE_TTL = 60 * 10  # 10 minutos


def get_usdt_pairs() -> List[str]:
    """
    Devuelve pares USDT activos en Binance Spot.
    Usa cache para NO llamar get_exchange_info() en cada scan.
    """
    global _USDT_CACHE, _USDT_CACHE_TS

    now = time.time()

    # ✅ cache válido
    if _USDT_CACHE and (now - _USDT_CACHE_TS) < _USDT_CACHE_TTL:
        return _USDT_CACHE

    client = Client(api_key=None, api_secret=None)

    # ✅ blindaje por timeout / caídas
    try:
        info = client.get_exchange_info()
    except Exception as e:
        # fallback si Binance falla
        print(f"[UNIVERSE ERROR] get_exchange_info failed: {e}")
        if _USDT_CACHE:
            return _USDT_CACHE
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

    symbols: List[str] = []
    for s in info.get("symbols", []):
        if (
            s.get("quoteAsset") == "USDT"
            and s.get("status") == "TRADING"
            and s.get("isSpotTradingAllowed", False)
        ):
            symbols.append(s["symbol"])

    # guardar cache
    _USDT_CACHE = symbols
    _USDT_CACHE_TS = now
    return symbols


def load_market_data(
    symbol: str,
    timeframe: str,
    limit: int = 200
) -> pd.DataFrame:
    """
    Carga OHLCV desde Binance Spot.
    Blindado contra valores inválidos y fallos de red.
    """

    # ✅ FIX: asegurar SIEMPRE int
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 200

    # Binance no acepta 0 o negativos
    if limit <= 0:
        limit = 200

    client = Client(api_key=None, api_secret=None)

    try:
        klines = client.get_klines(
            symbol=symbol,
            interval=timeframe,
            limit=limit
        )
    except Exception as e:
        print(f"[KLINES ERROR] {symbol}: {e}")
        return pd.DataFrame()

    if not klines:
        return pd.DataFrame()

    df = pd.DataFrame(
        klines,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    # ✅ Tipos numéricos
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df
