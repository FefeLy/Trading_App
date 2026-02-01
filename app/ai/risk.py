def adapt_risk(score):
    """
    Ajusta el riesgo según la calidad de la señal.
    """

    if score >= 0.8:
        return 0.01      # 1 %

    if score >= 0.6:
        return 0.005     # 0.5 %

    return 0.0           # NO TRADE
