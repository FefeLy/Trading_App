from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import csv
from pathlib import Path

router = APIRouter()

DATA_PATH = Path("app/data/journal.csv")

class TradeInput(BaseModel):
    symbol: str
    side: str
    entry: float
    stop: float
    take_profit: float
    risk_r: float
    profit_r: float
    rule_respected: bool

@router.post("/journal")
def save_trade(trade: TradeInput):
    with open(DATA_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.utcnow().isoformat(),
            trade.symbol,
            trade.side,
            trade.entry,
            trade.stop,
            trade.take_profit,
            trade.risk_r,
            trade.profit_r,
            trade.rule_respected
        ])

    return {"status": "saved"}

from app.journal.metrics import discipline_metrics

@router.get("/summary")
def journal_summary():
    return discipline_metrics()
