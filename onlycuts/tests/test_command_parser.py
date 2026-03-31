import pytest

from onlycuts.app.integrations.telegram.command_parser import (
    extract_ids_from_approval_message,
    parse_approval_command,
)


def test_parse_regen_with_modifier() -> None:
    parsed = parse_approval_command("regen stronger")
    assert parsed.action == "regen"
    assert parsed.modifier == "stronger"


def test_parse_queue_with_note() -> None:
    parsed = parse_approval_command("queue tomorrow 10:00")
    assert parsed.action == "queue"
    assert parsed.queue_note == "tomorrow 10:00"


def test_extract_ids_from_message_refs() -> None:
    text = "RefDraft: draft-123\nRefContent: content-456"
    draft_id, content_item_id = extract_ids_from_approval_message(text)
    assert draft_id == "draft-123"
    assert content_item_id == "content-456"


def test_parse_command_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        parse_approval_command("shipit")
