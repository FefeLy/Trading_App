from dataclasses import dataclass

@dataclass
class TradeResult:
    entry: float
    exit: float
    pnl: float
    rr: float
    win: bool
    duration: int

def execute_trade(df, signal):
    entry = df.iloc[-1]["close"]
    stop = signal.stop
    tp = signal.take_profit

    for i in range(len(df)):
        row = df.iloc[i]

        if row["low"] <= stop:
            return TradeResult(
                entry=entry,
                exit=stop,
                pnl=stop - entry,
                rr=-1,
                win=False,
                duration=i
            )

        if row["high"] >= tp:
            return TradeResult(
                entry=entry,
                exit=tp,
                pnl=tp - entry,
                rr=2,
                win=True,
                duration=i
            )

    return None

