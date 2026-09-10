"""FastAPI JSON API exposing the daily loldle answers."""

import time
from datetime import date
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from loldle import __version__
from loldle.cache import get_all_answers
from loldle.config import DEFAULT_REGION
from loldle.history import get_yesterday, save_today

app = FastAPI()

_CACHE_TTL_SECONDS = 300
_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _normalize_region(region: str) -> str:
    """Trim, lowercase and cap the region for upstream calls and cache keys."""
    return region.strip().lower()[:32]


def _build_payload(region: str) -> dict[str, Any]:
    """Fetch fresh answers for the region and assemble the /answers payload."""
    answers = get_all_answers(region)
    save_today(answers, region)
    return {
        "date": date.today().strftime("%d/%m/%Y"),
        "region": region,
        "answers": answers,
        "yesterday": get_yesterday() or None,
    }


def _get_payload(region: str) -> dict[str, Any]:
    """Serve the cached payload for a region, refreshing it after the TTL."""
    now = time.monotonic()
    cached = _cache.get(region)
    if cached is not None and now - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]
    payload = _build_payload(region)
    _cache[region] = (now, payload)
    return payload


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe kept dumb (no loldle call) because Dokploy polls it ~every 30s."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, Any]:
    """Service metadata and the endpoint list."""
    return {
        "service": "loldler-api",
        "version": __version__,
        "date": date.today().strftime("%d/%m/%Y"),
        "region": DEFAULT_REGION,
        "endpoints": ["/answers", "/health"],
    }


@app.get("/answers", response_model=None)
def answers(region: str = DEFAULT_REGION) -> dict[str, Any] | JSONResponse:
    """Return today's full answers for the region plus yesterday's, TTL-cached."""
    try:
        return _get_payload(_normalize_region(region))
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={"error": "upstream_failure", "detail": str(exc)},
        )
