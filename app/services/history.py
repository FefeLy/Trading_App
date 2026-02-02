import sqlite3
from pathlib import Path
from typing import Dict, Any

DB_PATH = Path("app/data/signals.db")

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS signal_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        symbol TEXT,
        timeframe TEXT,
        signal TEXT,
        strength TEXT,
        probability REAL,
        entry REAL,
        stop REAL,
        take_profit REAL,
        regime TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_signal_if_strong(payload: Dict[str, Any], min_prob: float = 0.75) -> bool:
    """
    Guarda SOLO si prob >= 0.75
    """
    try:
        prob = float(payload.get("probability") or 0.0)
    except Exception:
        prob = 0.0

    if prob < min_prob:
        return False

    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO signal_history (symbol, timeframe, signal, strength, probability, entry, stop, take_profit, regime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.get("symbol"),
        payload.get("timeframe"),
        payload.get("signal"),
        payload.get("strength"),
        prob,
        payload.get("entry"),
        payload.get("stop"),
        payload.get("take_profit"),
        payload.get("regime"),
    ))

    conn.commit()
    conn.close()
    return True
