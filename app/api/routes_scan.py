from fastapi import APIRouter, Query
from typing import Optional

from app.scanner.scanner import run_market_scan

router = APIRouter()

@router.get("/scan")
def scan_market(
    timeframe: str = Query("1h", description="Timeframe de análisis (ej: 1h, 4h)"),
    universe_size: int = Query(50, ge=10, le=300, description="Cantidad de pares USDT a escanear"),
    top_n: Optional[int] = Query(5, ge=1, le=20, description="Top N señales a devolver"),
):
    """
    Escanea el mercado USDT completo usando AI Scanner institucional
    y devuelve las mejores oportunidades rankeadas.

    Ejemplos:
    /scan
    /scan?timeframe=1h
    /scan?timeframe=1h&universe_size=50
    /scan?timeframe=1h&universe_size=50&top_n=5
    """

    return run_market_scan(
        timeframe=timeframe,
        universe_size=universe_size,
        top_n=top_n,
    )
