from dataclasses import dataclass


# =========================
# DATA STRUCTURE
# =========================
@dataclass
class TradePlan:
    entry: float
    stop: float
    take_profit: float
    position_size: float
    risk_pct: float
    probability: float


# =========================
# RISK MANAGER (EXECUTION ONLY)
# =========================
class RiskManager:
    """
    Risk manager institucional:
    - No modifica TP / SL
    - Solo valida y dimensiona posición
    """

    def __init__(
        self,
        base_risk_per_trade: float = 0.01,   # 1%
        max_risk_per_trade: float = 0.0125, # 1.25%
        min_probability: float = 0.60,
    ):
        self.base_risk = base_risk_per_trade
        self.max_risk = max_risk_per_trade
        self.min_probability = min_probability

    # =========================
    # RISK ADJUSTMENT
    # =========================
    def _risk_by_probability(self, probability: float) -> float:
        if probability < self.min_probability:
            return 0.0
        elif probability < 0.68:
            return self.base_risk * 0.5
        elif probability < 0.75:
            return self.base_risk
        else:
            return min(self.base_risk * 1.25, self.max_risk)

    # =========================
    # BUILD TRADE (NO PRICE LOGIC)
    # =========================
    def build_trade(
        self,
        capital: float,
        entry: float,
        stop: float,
        take_profit: float,
        probability: float,
    ) -> TradePlan | None:

        risk_pct = self._risk_by_probability(probability)
        if risk_pct == 0.0:
            return None

        risk_per_unit = abs(entry - stop)
        if risk_per_unit <= 0:
            return None

        capital_at_risk = capital * risk_pct
        position_size = capital_at_risk / risk_per_unit

        return TradePlan(
            entry=entry,
            stop=stop,
            take_profit=take_profit,
            position_size=position_size,
            risk_pct=risk_pct,
            probability=probability,
        )
