from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.data.loaders import load_market_data
from app.features.technicals import add_technicals
from app.signals.signal_engine import generate_signal

router = APIRouter()

# ========================================================
# SIGNAL POR PAR INDIVIDUAL
# ========================================================

@router.get("/signal")
def get_signal(
    symbol: str = Query(..., min_length=1, description="Trading pair e.g. BTCUSDT"),
    timeframe: str = Query("1h", min_length=1),
    limit: int = Query(200, ge=50, le=1000),
):
    try:
        # 1. Cargar datos de mercado
        df = load_market_data(symbol, timeframe, limit)

        if df is None or not isinstance(df, pd.DataFrame):
            raise HTTPException(
                status_code=502,
                detail="Market data provider returned invalid data",
            )

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No market data for {symbol} ({timeframe})",
            )

        required_columns = {"open", "high", "low", "close", "volume"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(
                status_code=500,
                detail="Market data missing required columns",
            )

        # 2. Indicadores técnicos
        df = add_technicals(df)

        if df is None or df.empty:
            raise HTTPException(
                status_code=422,
                detail="Not enough data after technical indicators",
            )

        # 3. Generar señal
        signal = generate_signal(df)

        if not isinstance(signal, dict):
            raise HTTPException(
                status_code=500,
                detail="Signal engine returned invalid format",
            )

        # 4. Sanitizar salida (JSON-safe)
        clean_signal = {}
        for key, value in signal.items():
            if hasattr(value, "item"):  # numpy / pandas scalar
                clean_signal[key] = value.item()
            else:
                clean_signal[key] = value

        clean_signal["symbol"] = symbol
        clean_signal["timeframe"] = timeframe

        return clean_signal

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Signal endpoint error: {str(e)}",
        )
