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
    assert parsed.content_item_id == "content-1234"


@pytest.mark.parametrize(
    "data",
    [
        "bad",
        "hack|draft-1234|content-1234",
        "post||content-1234",
        "post|draft-1234|",
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


def test_route_accepts_valid_flat_payload(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_data": "post|draft-1234|content-1234",
            "actor_user_id": 7,
            "actor_chat_id": 99,
            "callback_id": "cb-1",
        },
    )
    assert response.status_code == 200
    assert response.json()["action"] == "post"
    assert response.json()["accepted"] is True


def test_route_rejects_malformed_payload_shape(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post("/telegram/callback", json={"foo": "bar"})
    assert response.status_code == 400


def test_route_rejects_malformed_callback_data(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_data": "post|only-one-id",
            "actor_user_id": 7,
            "actor_chat_id": 99,
        },
    )
    assert response.status_code == 400


def test_route_supports_nested_envelope(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_query": {
                "id": "cb-2",
                "data": "post|draft-1234|content-1234",
                "actor_user_id": 7,
                "actor_chat_id": 99,
            }
        },
    )
    assert response.status_code == 200


def test_route_duplicate_callback_returns_idempotent(monkeypatch) -> None:
    duplicate_result = SimpleNamespace(effect="noop_duplicate", idempotent_replay=True)
    client = _build_client(monkeypatch, result=duplicate_result)
    response = client.post(
        "/telegram/callback",
        json={
            "callback_data": "post|draft-1234|content-1234",
            "actor_user_id": 7,
            "actor_chat_id": 99,
            "callback_id": "cb-dup",
        },
    )
    assert response.status_code == 200
    assert response.json()["idempotent"] is True
    assert response.json()["accepted"] is False
