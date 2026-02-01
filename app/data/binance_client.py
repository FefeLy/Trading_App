import pandas as pd
from binance.client import Client
from app.core.config import settings


# ============================
# Cliente Binance central
# ============================
def get_client() -> Client:
    """
    Devuelve un cliente Binance autenticado.
    """
    return Client(
        api_key=settings.BINANCE_API_KEY,
        api_secret=settings.BINANCE_API_SECRET
    )


# ============================
# Exchange Info (Universe base)
# ============================
def get_exchange_info() -> dict:
    """
    Wrapper institucional para obtener exchangeInfo.
    Usado por universe / filtros de mercado.
    """
    client = get_client()
    return client.get_exchange_info()


# ============================
# TOP 50 USDT por volumen (REAL)
# ============================
def get_top_usdt_pairs_by_volume(top_n: int = 50) -> list[str]:
    """
    Devuelve TOP pares USDT ordenados por volumen 24h (quoteVolume).
    Esto es lo más profesional para un scanner institucional.
    """
    client = get_client()

    # Exchange info para filtrar solo TRADING + USDT
    info = get_exchange_info()
    symbols_info = info.get("symbols", [])

    tradable_usdt = set()
    for s in symbols_info:
        try:
            sym = s.get("symbol", "")
            status = s.get("status", "")
            quote = s.get("quoteAsset", "")

            if status != "TRADING":
                continue
            if quote != "USDT":
                continue
            if not sym.endswith("USDT"):
                continue

            # excluir cosas raras si quieres (UP/DOWN tokens)
            if sym.endswith("UPUSDT") or sym.endswith("DOWNUSDT"):
                continue

            tradable_usdt.add(sym)
        except Exception:
            continue

    # 24h tickers
    tickers = client.get_ticker()  # trae volume + quoteVolume por símbolo

    ranked = []
    for t in tickers:
        try:
            sym = t.get("symbol", "")
            if sym not in tradable_usdt:
                continue

            # quoteVolume = volumen en USDT (mejor para ranking institucional)
            qv = float(t.get("quoteVolume", 0.0) or 0.0)
            ranked.append((sym, qv))
        except Exception:
            continue

    # ordenar desc por quoteVolume
    ranked.sort(key=lambda x: x[1], reverse=True)

    top_symbols = [sym for sym, _ in ranked[: max(1, int(top_n))]]
    return top_symbols


# ============================
# Cargar velas (klines)
# ============================
def load_market_data(symbol: str, timeframe: str = "1h", limit: int = 200) -> pd.DataFrame:
    """
    Descarga velas (klines) y devuelve DataFrame estándar:
    open, high, low, close, volume
    """
    client = get_client()

    klines = client.get_klines(symbol=symbol, interval=timeframe, limit=int(limit))
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
            "num_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    # Convertir a float
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Timestamps (por si lo necesitas en UI)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", errors="coerce")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", errors="coerce")

    df = df.dropna(subset=["open", "high", "low", "close", "volume"])
    return df.reset_index(drop=True)
