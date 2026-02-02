def confidence_score(probability: float) -> float:
    """
    Convierte probabilidad en nivel de confianza (0–1)
    """
    return abs(probability - 0.5) * 2
