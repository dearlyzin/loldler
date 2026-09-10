import json
import time

import httpx

from loldle.config import (
    CACHE_URL,
    DEFAULT_REGION,
    KEY_ANSWERS,
    KEY_RESPONSE_BODY,
    MODES,
    USER_AGENT,
)
from loldle.crypto import decrypt


def fetch_raw_cache() -> str:
    """Fetch the encrypted cache.json from loldle."""
    resp = httpx.get(
        CACHE_URL,
        params={"_": str(int(time.time() * 1000))},
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=10.0,
    )
    resp.raise_for_status()
    return resp.text


def decrypt_cache(raw: str) -> dict:
    """Decrypt the entire cache.json body."""
    return json.loads(decrypt(raw, KEY_RESPONSE_BODY))


def _extract_answers(parsed: dict, region: str = DEFAULT_REGION) -> dict[str, dict]:
    """Extract and decrypt all answers for a given region."""
    answers = {}
    for mode in MODES:
        key = f"{mode}_answerEncrypted_{region}"
        if key in parsed:
            try:
                decrypted = decrypt(parsed[key], KEY_ANSWERS)
                answers[mode] = json.loads(decrypted)
            except Exception:
                answers[mode] = {"error": True}
        else:
            answers[mode] = {"error": True}
    return answers


def get_all_answers(region: str = DEFAULT_REGION) -> dict[str, dict]:
    """Fetch + decrypt + extract all answers for a region."""
    raw = fetch_raw_cache()
    parsed = decrypt_cache(raw)
    return _extract_answers(parsed, region)
