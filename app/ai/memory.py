import json
from pathlib import Path

MEMORY_FILE = Path("data/trade_memory.json")


def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []


def save_trade(trade):
    memory = load_memory()
    memory.append(trade)
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))
