from binance.client import Client
import pandas as pd

from app.data.cache import get_cached, set_cached

INTERVAL_MAP = {
    "1m": Client.KLINE_INTERVAL_1MINUTE,
    "5m": Client.KLINE_INTERVAL_5MINUTE,
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR,
    "4h": Client.KLINE_INTERVAL_4HOUR,
    "1d": Client.KLINE_INTERVAL_1DAY,
}

def load_market_data(symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
    cache_key = f"{symbol}:{timeframe}:{limit}"

    # 1️⃣ CACHE
    cached = get_cached(cache_key)
    if cached is not None:
        if isinstance(cached, pd.DataFrame):
            return cached
        else:
            return pd.DataFrame()

    # 2️⃣ TODO LO DEMÁS VA DENTRO DEL TRY
    try:
        if timeframe not in INTERVAL_MAP:
            return pd.DataFrame()

        client = Client(api_key=None, api_secret=None)

        klines = client.get_klines(
            symbol=symbol,
            interval=INTERVAL_MAP[timeframe],
            limit=limit,
        )

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

        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

        df = df.sort_values("open_time").reset_index(drop=True)

        set_cached(cache_key, df)
        return df

    except Exception:
        # 3️⃣ FALLBACK FINAL SEGURO
        return pd.DataFrame()
