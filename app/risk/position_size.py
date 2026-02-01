def calculate_position_size(
    capital: float,
    risk_per_trade: float,
    entry_price: float,
    stop_price: float
) -> float:
    """
    capital: capital total
    risk_per_trade: % del capital a arriesgar (ej: 0.01 = 1%)
    entry_price: precio de entrada
    stop_price: precio de stop loss
    """

    risk_amount = capital * risk_per_trade
    risk_per_unit = abs(entry_price - stop_price)

    if risk_per_unit == 0:
        return 0

    position_size = risk_amount / risk_per_unit
    return position_size

def compute_position_size(
    equity: float,
    risk_pct: float,
    entry: float,
    stop: float
) -> float:
    """
    Tamaño en unidades del activo (spot/contrato teórico).
    """
    if entry <= 0 or stop <= 0 or entry == stop:
        return 0.0

    risk_capital = equity * risk_pct
    stop_distance = abs(entry - stop)

    return round(risk_capital / stop_distance, 6)

def compute_position_size(
    equity: float,
    risk_pct: float,
    entry: float,
    stop: float
) -> float:
    if equity <= 0 or risk_pct <= 0:
        return 0.0
    if entry <= 0 or stop <= 0 or entry == stop:
        return 0.0

    risk_amount = equity * risk_pct
    stop_distance = abs(entry - stop)

    return round(risk_amount / stop_distance, 6)
