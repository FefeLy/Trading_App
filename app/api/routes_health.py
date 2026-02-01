from fastapi import APIRouter
from app.db.session import SessionLocal
from app.signals.signal_engine import generate_signal

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health():
    db_ok = True
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception:
        db_ok = False

    signal_engine_ok = True
    try:
        _ = generate_signal
    except Exception:
        signal_engine_ok = False

    return {
        "status": "ok" if db_ok and signal_engine_ok else "degraded",
        "db": db_ok,
        "signal_engine": signal_engine_ok
    }

