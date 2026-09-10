import os
from pathlib import Path

CACHE_URL = "https://cache.loldle.net/cache.json"
KEY_RESPONSE_BODY = "D5XCtTOObw"
KEY_ANSWERS = "QhDZJfngdx"
DEFAULT_REGION = "america"

MODES = ["classic", "quote", "ability", "emoji", "splash"]

MODE_LABELS = {
    "classic": "Classic",
    "quote": "Quote",
    "ability": "Ability",
    "emoji": "Emoji",
    "splash": "Splash Art",
}

HISTORY_DIR = Path(
    (os.environ.get("LOLDLE_HISTORY_DIR") or "").strip()
    or str(Path.home() / ".loldle-resolver")
)
HISTORY_FILE = HISTORY_DIR / "history.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0.0.0 Safari/537.36"
)
