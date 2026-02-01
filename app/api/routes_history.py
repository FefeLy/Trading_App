from fastapi import APIRouter
from typing import List, Dict, Any
import json
from pathlib import Path
from datetime import datetime

router = APIRouter()

HISTORY_FILE = Path("app/data/signal_history.json")
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def _load_history() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

def _save_history(items: List[Dict[str, Any]]):
    HISTORY_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")

@router.get("/history")
def get_history(limit: int = 50):
    data = _load_history()
    return {
        "status": "ok",
        "count": len(data),
        "items": data[-limit:][::-1]  # últimos primero
    }

@router.delete("/history")
def clear_history():
    _save_history([])
    return {"status": "ok", "cleared": True}
