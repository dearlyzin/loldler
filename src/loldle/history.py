import json
from datetime import date, timedelta

from loldle.config import HISTORY_DIR, HISTORY_FILE


def _ensure_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _today_str() -> str:
    return date.today().isoformat()


def save_today(answers: dict, region: str) -> None:
    """Save today's answers to local history."""
    _ensure_dir()
    history = load_history()
    today = _today_str()
    entry = {"date": today, "region": region}
    for mode, data in answers.items():
        entry[mode] = data.get("champion_name", "?")
    history = [e for e in history if e["date"] != today]
    history.append(entry)
    _write(history)


def load_history() -> list[dict]:
    """Load local history file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def get_yesterday() -> dict[str, str]:
    """Return yesterday's answers, if available."""
    history = load_history()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    for entry in reversed(history):
        if entry["date"] == yesterday:
            modes = {"classic", "quote", "ability", "emoji", "splash"}
            return {k: v for k, v in entry.items() if k in modes}
    return {}


def _write(history: list[dict]) -> None:
    _ensure_dir()
    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
