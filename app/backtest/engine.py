import pandas as pd

from app.data.loaders import load_market_data
from app.features import build_features
from app.signals.signal_engine import SignalEngine
from app.services.risk_service import enrich_signal_with_risk
from app.core.logger import get_logger


logger = get_logger(__name__)


def run_backtest(
    symbol: str,
    timeframe: str,
    initial_equity: float = 10_000.0,
) -> pd.DataFrame:
    equity = float(initial_equity)
    equity_curve = []

    # position:
    # {
    #   "side": "LONG" or "SHORT",
    #   "entry": float,
    #   "size": float,
    #   "stop": float
    # }
    position = None

    # ✅ normalizar timeframe por seguridad (evita 1h1h)
    timeframe = (timeframe or "1h").strip()
    if len(timeframe) % 2 == 0 and timeframe[: len(timeframe) // 2] == timeframe[len(timeframe) // 2 :]:
        timeframe = timeframe[: len(timeframe) // 2]

    df = load_binance_klines(symbol, timeframe)
    if df is None or df.empty:
        logger.warning(f"No data for {symbol} {timeframe}")
        return pd.DataFrame([])

    df = build_features(df)

    engine = SignalEngine(threshold=0.55)

    for i in range(100, len(df)):
        window = df.iloc[:i].copy()
        price = float(window.iloc[-1]["close"])

        # ✅ Generar señal ML
        raw_signal = engine.generate(window)

        # ✅ Enriquecer con gestión de riesgo
        signal = enrich_signal_with_risk(
            raw_signal,
            equity=equity,
            current_dd=0.0,
        )

        sig = signal.get("signal")

        # -----------------------------------------------------
        # ✅ ENTRADAS
        # -----------------------------------------------------
        if position is None:
            if sig == "BUY":
                position = {
                    "side": "LONG",
                    "entry": price,
                    "size": float(signal.get("position_size", 0) or 0),
                    "stop": float(signal.get("stop") or price),
                }
                logger.info(f"[LONG OPEN] {symbol} entry={price}")

            elif sig == "SELL":
                position = {
                    "side": "SHORT",
                    "entry": price,
                    "size": float(signal.get("position_size", 0) or 0),
                    "stop": float(signal.get("stop") or price),
                }
                logger.info(f"[SHORT OPEN] {symbol} entry={price}")

        # -----------------------------------------------------
        # ✅ SALIDAS POR STOP LOSS
        # -----------------------------------------------------
        else:
            side = position["side"]
            entry = float(position["entry"])
            size = float(position["size"])
            stop = float(position["stop"])

            if size <= 0:
                # si risk_service devolvió size inválido, cerramos
                position = None
            else:
                # LONG: stop se activa si price <= stop
                if side == "LONG" and price <= stop:
                    pnl = (price - entry) * size
                    equity += pnl
                    logger.info(f"[LONG STOP] {symbol} pnl={pnl:.2f} equity={equity:.2f}")
                    position = None

                # SHORT: stop se activa si price >= stop
                elif side == "SHORT" and price >= stop:
                    pnl = (entry - price) * size
                    equity += pnl
                    logger.info(f"[SHORT STOP] {symbol} pnl={pnl:.2f} equity={equity:.2f}")
                    position = None

        equity_curve.append(
            {
                "timestamp": window.index[-1],
                "equity": equity,
                "price": price,
                "position": position["side"] if position else None,
            }
        )

    return pd.DataFrame(equity_curve)

