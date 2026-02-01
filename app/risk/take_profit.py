from app.core.signal_types import SignalType

RISK_REWARD = 2.0

def compute_take_profit(price: float, stop_loss: float, signal: SignalType) -> float:
    """
    Take profit institucional:
    - BUY: RR clásico
    - SELL: RR inverso
    - HOLD: proyección de rango
    """

    risk = abs(price - stop_loss)

    if signal == SignalType.BUY:
        return round(price + risk * RISK_REWARD, 4)

    if signal == SignalType.SELL:
        return round(price - risk * RISK_REWARD, 4)

    # HOLD institucional
    return round(price + risk, 4)
