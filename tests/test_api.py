"""Tests for the FastAPI service in api.py."""

from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient

from loldle import api

FAKE_ANSWERS: dict[str, dict] = {
    "classic": {"champion_name": "Gwen", "clues": {"quote": {"name": "Hallowed Mist"}}},
    "quote": {"champion_name": "Jinx", "question": "Who says this?"},
    "ability": {
        "champion_name": "Yasuo",
        "ability_name": "Steel Tempest",
        "ability_letter": "Q",
    },
    "emoji": {"champion_name": "Zed", "title": "The Master of Shadows"},
    "splash": {"champion_name": "Lux", "splash_name": "Arcade Lux"},
}


@pytest.fixture(autouse=True)
def _clear_cache() -> Iterator[None]:
    """Clear the module TTL cache between tests."""
    api._cache.clear()
    yield
    api._cache.clear()


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient against the api app."""
    return TestClient(api.app)


def test_answers_returns_full_payload_with_passthrough(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(api, "get_all_answers", lambda region: FAKE_ANSWERS)
    monkeypatch.setattr(api, "save_today", lambda answers, region: None)
    monkeypatch.setattr(api, "get_yesterday", lambda: {"classic": "Gwen", "quote": "Jinx"})

    resp = client.get("/answers")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"date", "region", "answers", "yesterday"}
    assert body["answers"] == FAKE_ANSWERS
    assert body["yesterday"] == {"classic": "Gwen", "quote": "Jinx"}
    assert body["region"] == "america"
    assert body["date"] == date.today().strftime("%d/%m/%Y")


def test_answers_serves_ttl_cache_on_second_get(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    saves: list[str] = []

    def fake_fetch(region: str) -> dict[str, dict]:
        calls.append(region)
        return FAKE_ANSWERS

    monkeypatch.setattr(api, "get_all_answers", fake_fetch)
    monkeypatch.setattr(api, "save_today", lambda answers, region: saves.append(region))
    monkeypatch.setattr(api, "get_yesterday", lambda: {})

    first = client.get("/answers")
    second = client.get("/answers")

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(calls) == 1
    assert saves == ["america"]
    assert second.json()["answers"] == FAKE_ANSWERS


def test_upstream_failure_returns_502_and_is_not_cached(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = {"fail": True}

    def fake_fetch(region: str) -> dict[str, dict]:
        if state["fail"]:
            raise RuntimeError("loldle down")
        return FAKE_ANSWERS

    monkeypatch.setattr(api, "get_all_answers", fake_fetch)
    monkeypatch.setattr(api, "save_today", lambda answers, region: None)
    monkeypatch.setattr(api, "get_yesterday", lambda: {})

    first = client.get("/answers")

    assert first.status_code == 502
    assert first.json() == {"error": "upstream_failure", "detail": "loldle down"}

    state["fail"] = False
    second = client.get("/answers")

    assert second.status_code == 200
    assert second.json()["answers"] == FAKE_ANSWERS


def test_region_is_normalized(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_fetch(region: str) -> dict[str, dict]:
        seen.append(region)
        return FAKE_ANSWERS

    monkeypatch.setattr(api, "get_all_answers", fake_fetch)
    monkeypatch.setattr(api, "save_today", lambda answers, region: None)
    monkeypatch.setattr(api, "get_yesterday", lambda: {})

    resp = client.get("/answers", params={"region": "EUROPE "})

    assert resp.status_code == 200
    assert resp.json()["region"] == "europe"
    assert seen == ["europe"]


def test_unknown_path_returns_404(client: TestClient) -> None:
    assert client.get("/nope").status_code == 404


def test_health_and_root_shapes(client: TestClient) -> None:
    health = client.get("/health")
    root = client.get("/")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert root.status_code == 200
    assert root.json() == {
        "service": "loldler-api",
        "version": api.__version__,
        "date": date.today().strftime("%d/%m/%Y"),
        "region": api.DEFAULT_REGION,
        "endpoints": ["/answers", "/health"],
    }
