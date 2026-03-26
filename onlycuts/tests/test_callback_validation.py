from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from onlycuts.app.api import telegram_callbacks as callbacks_module
from onlycuts.app.api.telegram_callbacks import router
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data


def test_callback_parse_success() -> None:
    parsed = parse_callback_data("post|draft-1234|content-1234")
    assert parsed.action == "post"
    assert parsed.draft_id == "draft-1234"


@pytest.mark.parametrize(
    "data",
    [
        "bad",
        "post||content-1234",
        "post|draft-1234|",
        "hack|draft-1234|content-1234",
        "post|draft-1234",
    ],
)
def test_callback_parse_invalid_variants(data: str) -> None:
    with pytest.raises(Exception):
        parse_callback_data(data)


def _build_client(monkeypatch, result=None):
    @contextmanager
    def _scope():
        class StubService:
            def resolve_action(self, **_kwargs):
                return result or SimpleNamespace(effect="published", idempotent_replay=False)

        class StubSession:
            def commit(self):
                return None

        yield StubService(), StubSession()

    monkeypatch.setattr(callbacks_module, "approval_service_scope", _scope)
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_callback_route_accepts_valid_payload(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_query": {
                "id": "cb-1",
                "data": "post|draft-1234|content-1234",
                "from_user": {"id": 7},
                "message": {"chat": {"id": 99}},
            }
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["action"] == "post"


def test_callback_route_rejects_bad_shape(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post("/telegram/callback", json={"foo": "bar"})
    assert response.status_code == 422


def test_callback_route_rejects_malformed_data(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_query": {
                "id": "cb-1",
                "data": "post|only-one-id",
                "from_user": {"id": 7},
                "message": {"chat": {"id": 99}},
            }
        },
    )
    assert response.status_code == 400


def test_callback_route_reports_duplicate_idempotency(monkeypatch) -> None:
    duplicate_result = SimpleNamespace(effect="noop_duplicate", idempotent_replay=True)
    client = _build_client(monkeypatch, result=duplicate_result)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_query": {
                "id": "cb-dup",
                "data": "post|draft-1234|content-1234",
                "from_user": {"id": 7},
                "message": {"chat": {"id": 99}},
            }
        },
    )
    assert response.status_code == 200
    assert response.json()["idempotent"] is True
    assert response.json()["accepted"] is False
