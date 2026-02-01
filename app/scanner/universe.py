# app/scanner/universe.py

from app.data.binance_client import get_exchange_info


def get_usdt_universe() -> list[str]:
    """
    Devuelve todos los pares USDT spot activos en Binance.
    Ej: BTCUSDT, ETHUSDT, SOLUSDT, etc.
    """

    info = get_exchange_info()

    symbols = []

    for s in info["symbols"]:
        if (
            s["quoteAsset"] == "USDT"
            and s["status"] == "TRADING"
            and s["isSpotTradingAllowed"]
        ):
            symbols.append(s["symbol"])

    return symbols
