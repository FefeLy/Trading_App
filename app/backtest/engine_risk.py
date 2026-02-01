import pandas as pd
from app.signals.signal_engine import SignalType

class RiskBacktestEngine:

    def __init__(self, initial_capital: float = 10_000):
        self.initial_capital = initial_capital

    def run(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
        trade_plans: dict
    ) -> pd.DataFrame:

        capital = self.initial_capital
        equity = []
        position_size = 0
        entry = stop = take_profit = None
        in_position = False

        for i in range(len(df) - 1):
            price = df.iloc[i]["close"]
            next_price = df.iloc[i + 1]["close"]
            signal = signals.iloc[i]

            # ENTRY
            if signal == SignalType.BUY and not in_position:
                plan = trade_plans.get(i)
                if plan is not None:
                    position_size = plan.position_size
                    entry = plan.entry
                    stop = plan.stop
                    take_profit = plan.take_profit
                    in_position = True

            # EXIT CONDITIONS
            if in_position:
                if next_price <= stop:
                    capital += position_size * stop
                    in_position = False
                    position_size = 0

                elif next_price >= take_profit:
                    capital += position_size * take_profit
                    in_position = False
                    position_size = 0

            # EQUITY
            current_equity = capital
            if in_position:
                current_equity += position_size * next_price

            equity.append(current_equity)

        df_bt = df.iloc[:len(equity)].copy()
        df_bt["equity"] = equity
        df_bt["returns"] = df_bt["equity"].pct_change().fillna(0)

        return df_bt
