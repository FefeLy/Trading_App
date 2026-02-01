# app/ai/threshold.py

from __future__ import annotations
from typing import Tuple

from app.ai.regime import MarketRegime


def get_dynamic_threshold(regime: MarketRegime) -> Tuple[float, float]:
    """
    Devuelve SIEMPRE dos valores:
      (threshold_strong, threshold_weak)

    Nunca devuelve None.
    Esto evita:
      cannot unpack non-iterable NoneType object
    """

    # Defaults seguros
    threshold_strong = 0.70
    threshold_weak = 0.50

    try:
        if regime == MarketRegime.TRENDING:
            threshold_strong = 0.72
            threshold_weak = 0.53

        elif regime == MarketRegime.RANGING:
            threshold_strong = 0.75
            threshold_weak = 0.58

        else:
            # Mercado caótico u otro estado -> más estricto, pero NUNCA None
            threshold_strong = 0.78
            threshold_weak = 0.60

        # Blindaje final
        threshold_strong = float(threshold_strong)
        threshold_weak = float(threshold_weak)

        # Asegurar orden lógico
        if threshold_weak >= threshold_strong:
            threshold_weak = threshold_strong - 0.10

        return threshold_strong, threshold_weak

    except Exception:
        return 0.70, 0.50
