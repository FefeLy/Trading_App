import pandas as pd
from app.signals.signal_engine import SignalType

class BacktestEngine:

    def __init__(
        self,
        initial_capital: float = 10_000,
        position_size: float = 1.0
    ):
        self.initial_capital = initial_capital
        self.position_size = position_size

    def run(self, df: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
        capital = self.initial_capital
        equity = []
        position = 0
        entry_price = 0

        for i in range(len(df) - 1):
            price = df.iloc[i]["close"]
            next_price = df.iloc[i + 1]["close"]
            signal = signals.iloc[i]

            # ENTRY
            if signal == SignalType.BUY and position == 0:
                position = (capital * self.position_size) / price
                entry_price = price
                capital = 0

            # EXIT
            elif signal == SignalType.SELL and position > 0:
                capital = position * price
                position = 0

            # Equity calculation
            current_equity = capital + position * next_price
            equity.append(current_equity)

        df_bt = df.iloc[:len(equity)].copy()
        df_bt["equity"] = equity
        df_bt["returns"] = df_bt["equity"].pct_change().fillna(0)

        return df_bt
