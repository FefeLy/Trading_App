from pydantic import BaseModel
from typing import Literal, Optional


class SignalOut(BaseModel):
    symbol: str
    timeframe: str
    signal: Literal["BUY", "SELL", "HOLD"]

    entry: Optional[float] = None
    stop: Optional[float] = None
    take_profit: Optional[float] = None

    risk_per_trade_pct: Optional[float] = None
    position_size: Optional[float] = None
    r_multiple_target: Optional[float] = None

    reason: Optional[str] = None
