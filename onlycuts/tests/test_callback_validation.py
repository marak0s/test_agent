from contextlib import contextmanager
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from onlycuts.app.api import telegram_callbacks as callbacks_module
from onlycuts.app.api.telegram_callbacks import router
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data
from onlycuts.app.integrations.telegram.command_parser import extract_ids_from_approval_message, parse_approval_command


def test_callback_parse_success() -> None:
    parsed = parse_callback_data("post|draft-1234|content-1234")
    assert parsed.action == "post"


@pytest.mark.parametrize("data", ["bad", "hack|draft-1234|content-1234", "post||content-1234", "post|draft-1234|"])
def test_callback_parse_invalid_variants(data: str) -> None:
    with pytest.raises(Exception):
        parse_callback_data(data)


def test_reply_command_parse_success() -> None:
    parsed = parse_approval_command("queue tomorrow 10:00")
    assert parsed.action == "queue"
    assert parsed.queue_note == "tomorrow 10:00"


def test_reply_command_invalid() -> None:
    with pytest.raises(ValueError):
        parse_approval_command("shipit")


def test_extract_refs_missing() -> None:
    with pytest.raises(ValueError):
        extract_ids_from_approval_message("no refs")


def _build_client(monkeypatch, *, result=None, unauthorized=False):
    @contextmanager
    def _scope():
        class StubService:
            def resolve_action(self, **_kwargs):
                if unauthorized:
                    raise callbacks_module.AuthorizationError("not allowed")
                return result or SimpleNamespace(effect="published", idempotent_replay=False)

            def resolve_reply_command(self, **_kwargs):
                if unauthorized:
                    raise callbacks_module.AuthorizationError("not allowed")
                return result or SimpleNamespace(effect="published", idempotent_replay=False)

        class StubSession:
            def commit(self):
                return None

        yield StubService(), StubSession()

    monkeypatch.setattr(callbacks_module, "approval_service_scope", _scope)
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_route_callback_malformed_payload(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post("/telegram/callback", json={"foo": "bar"})
    assert response.status_code == 400


def test_route_callback_malformed_data(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={"callback_data": "post|bad", "actor_user_id": 7, "actor_chat_id": 9},
    )
    assert response.status_code == 400


def test_route_reply_malformed_payload(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={"message": {"message_id": 1, "text": "post", "actor_user_id": 7, "actor_chat_id": 9}},
    )
    assert response.status_code == 400


def test_route_reply_dispatches_to_service(monkeypatch) -> None:
    client = _build_client(monkeypatch)
    response = client.post(
        "/telegram/callback",
        json={
            "message": {
                "message_id": 11,
                "text": "post",
                "actor_user_id": 7,
                "actor_chat_id": 9,
                "reply_to_message": {"text": "RefDraft: draft-1234\nRefContent: content-1234"},
            }
        },
    )
    assert response.status_code == 200
    assert response.json()["action"] == "post"


def test_route_callback_unauthorized(monkeypatch) -> None:
    client = _build_client(monkeypatch, unauthorized=True)
    response = client.post(
        "/telegram/callback",
        json={"callback_data": "post|draft-1234|content-1234", "actor_user_id": 999, "actor_chat_id": 9},
    )
    assert response.status_code == 403
