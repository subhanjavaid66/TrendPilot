
import json
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path(__file__).parent / "history.json"


def load_history():

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_history(result):

    history = load_history()

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": result["plan"]["topic"],
        "content": result["content"],
        "analysis": result["analysis"],
        "review": result["review"]
    }

    history.append(record)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)

    return record


def get_history():

    return load_history()
