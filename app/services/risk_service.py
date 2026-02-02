from app.core.constants import R_TARGET
from app.risk.drawdown_control import adjust_risk_by_drawdown
from app.risk.position_size import compute_position_size
from app.core.logger import get_logger

logger = get_logger(__name__)
logger.info("Signal generated")

def enrich_signal_with_risk(signal: dict, equity: float, current_dd: float) -> dict:
    if signal.get("signal") == "HOLD":
        return signal

    risk_pct = adjust_risk_by_drawdown(current_dd)

    if risk_pct <= 0:
        signal["signal"] = "HOLD"
        signal["reason"] = "drawdown_limit"
        return signal

    entry = signal["entry"]
    stop = signal["stop"]

    size = compute_position_size(equity, risk_pct, entry, stop)

    signal.update({
        "risk_per_trade_pct": risk_pct,
        "position_size": size,
        "r_multiple_target": R_TARGET
    })

    return signal

def compute_take_profit(
    entry: float,
    stop: float,
    r_multiple: float = 2.0
) -> float:
    """
    Wrapper estándar usado por SignalEngine.
    """
    return take_profit_price(
        entry_price=entry,
        stop_price=stop,
        rr_ratio=r_multiple
    )
