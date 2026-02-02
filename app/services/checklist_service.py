from datetime import datetime
from typing import Dict

def daily_checklist(signal: Dict, market_ok: bool, news_ok: bool) -> Dict:
    """
    Checklist previo a ejecutar un trade MANUAL.
    Devuelve pass/fail + razones.
    """

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "passed": True
    }

    def check(name: str, condition: bool):
        results["checks"][name] = condition
        if not condition:
            results["passed"] = False

    # 1️⃣ Señal válida
    check("signal_not_hold", signal.get("signal") in ("BUY", "SELL"))

    # 2️⃣ Confianza mínima
    check(
        "confidence_ok",
        signal.get("confidence") is not None and signal["confidence"] >= 0.10
    )

    # 3️⃣ Riesgo calculado
    check(
        "risk_defined",
        signal.get("risk_pct") is not None and signal.get("position_size", 0) > 0
    )

    # 4️⃣ Drawdown permitido (ya filtrado en riesgo, doble seguro)
    check(
        "risk_allowed",
        signal.get("signal") != "HOLD" or signal.get("reason") != "drawdown_limit"
    )

    # 5️⃣ Condiciones externas
    check("market_conditions_ok", market_ok)
    check("news_ok", news_ok)

    return results
