from app.risk.drawdown_control import adjust_risk_by_drawdown
from app.risk.position_size import compute_position_size
from app.core.constants import R_TARGET

def enrich_signal_with_risk(
    signal: dict,
    equity: float,
    current_dd: float
) -> dict:

    if signal["signal"] == "HOLD":
        return signal

    risk_pct = adjust_risk_by_drawdown(current_dd)

    if risk_pct == 0:
        signal["signal"] = "HOLD"
        signal["reason"] = "drawdown_limit"
        return signal

    entry = signal.get("entry")
    stop = signal.get("stop")

    size = compute_position_size(equity, risk_pct, entry, stop)

    signal.update({
        "risk_pct": risk_pct,
        "position_size": size,
        "r_target": R_TARGET
    })

    return signal
