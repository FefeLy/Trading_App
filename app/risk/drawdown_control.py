from app.core.constants import BASE_RISK_PCT, MIN_RISK_PCT, DD_SOFT, DD_HARD

def adjust_risk_by_drawdown(current_dd: float) -> float:
    """
    current_dd en [0,1] (ej. 0.12 = 12%)
    """
    if current_dd >= DD_HARD:
        return 0.0
    if current_dd >= DD_SOFT:
        return MIN_RISK_PCT
    return BASE_RISK_PCT
