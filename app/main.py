from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from app.api.routes_history import router as history_router

# ======================
# App
# ======================
app = FastAPI(title="Trading Signal API")

from app.services.history import init_db

init_db()

# ======================
# Routers
# ======================
from app.api.routes_journal import router as journal_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_signal import router as signal_router
from app.api.routes_health import router as health_router
from app.api.routes_scan import router as scan_router

app.include_router(scan_router)
app.include_router(journal_router)
app.include_router(dashboard_router)
app.include_router(signal_router)
app.include_router(health_router)
app.include_router(history_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# ======================
# Schemas (NO TOCAR)
# ======================
class SignalResponse(BaseModel):
    signal: str
    probability: float
    confidence: float
    entry: float | None = None
    stop: float | None = None
    take_profit: float | None = None
    position_size: float | None = None

# ======================
# Root (Frontend)
# ======================
@app.get("/", response_class=HTMLResponse)
def app_root():
    return Path("app/templates/index.html").read_text(encoding="utf-8")
