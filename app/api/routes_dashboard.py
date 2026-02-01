from fastapi import APIRouter
from sqlalchemy import func

from app.db.session import SessionLocal
from app.db.models import TradeJournal

from app.backtest.engine import run_backtest
from app.backtest.metrics import compute_metrics
from app.backtest.report import build_report
from app.signals.signal_engine import SignalEngine

from app.data.loaders import load_market_data
from app.data.cleaners import clean_market_data
from app.features.technicals import add_technicals
from app.journal.equity import equity_curve

from app.backtest.metrics import (
    compute_expectancy,
    compute_profit_factor,
    compute_risk_score
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# =========================
# SUMMARY (disciplina real)
# =========================
@router.get("/summary")
def dashboard_summary():
    db = SessionLocal()

    trades = db.query(TradeJournal).all()
    total_trades = len(trades)

    wins = [t for t in trades if t.pnl and t.pnl > 0]
    losses = [t for t in trades if t.pnl and t.pnl <= 0]

    total_pnl = sum(t.pnl for t in trades if t.pnl)
    win_rate = round(len(wins) / total_trades, 2) if total_trades > 0 else 0

    last_trade = trades[-1] if trades else None

    db.close()

    return {
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "total_pnl": round(total_pnl, 2),
        "last_trade": {
            "symbol": last_trade.symbol,
            "pnl": last_trade.pnl,
            "date": last_trade.created_at
        } if last_trade else None
    }

# =========================
# EQUITY (journal real)
# =========================
@router.get("/equity")
def equity_curve(initial_capital: float = 10_000):
    db = SessionLocal()

    trades = db.query(TradeJournal).order_by(TradeJournal.created_at).all()

    equity = initial_capital
    curve = []

    for t in trades:
        if t.pnl:
            equity += t.pnl
            curve.append({
                "date": t.created_at,
                "equity": round(equity, 2)
            })

    db.close()
    return curve

# =========================
# BACKTEST (simulación)
# =========================
@router.get("/backtest")
def dashboard_backtest(symbol: str = "BTCUSDT", timeframe: str = "1h"):
    df = load_binance_klines(symbol, timeframe, 1000)
    df = clean_market_data(df)
    df = add_technicals(df)

    engine = BacktestEngine(SignalEngine())
    trades = engine.run(df)

    metrics = compute_metrics(trades)
    report = build_report(trades, metrics)

    return report

@router.get("/market-price")
def market_price(symbol: str = "BTCUSDT"):
    from app.data.loaders import load_binance_price
    return {
        "symbol": symbol,
        "price": load_binance_price(symbol)
    }

@router.get("/backtest")
def backtest():
    from app.backtest.runner import run_backtest
    return run_backtest()

@router.get("/dashboard/backtest")
def run_backtest_endpoint():
    from app.backtest.runner import run_backtest

    result = run_backtest()

    trades = result["trades"]
    equity = result["equity"]
    max_dd = result["metrics"]["max_drawdown"]

    result["metrics"]["expectancy"] = compute_expectancy(trades)
    result["metrics"]["profit_factor"] = compute_profit_factor(trades)
    result["metrics"]["risk_score"] = compute_risk_score(trades, max_dd)

    return result


@router.get("/backtest")
def run_backtest():
    from app.backtest.runner import run_backtest

    result = run_backtest()

    trades = result["trades"]
    equity = result["equity"]

    max_dd = result["metrics"]["max_drawdown"]

    result["metrics"]["expectancy"] = compute_expectancy(trades)
    result["metrics"]["profit_factor"] = compute_profit_factor(trades)
    result["metrics"]["risk_score"] = compute_risk_score(trades, max_dd)

    return result


@router.get("/equity")
def get_equity_curve():
    return equity_curve()

