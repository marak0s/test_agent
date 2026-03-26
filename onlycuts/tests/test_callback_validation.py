import pytest

from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data


def test_callback_parse_success() -> None:
    parsed = parse_callback_data("post|draft-1234|content-1234")
    assert parsed.action == "post"


def test_callback_parse_invalid_format() -> None:
    with pytest.raises(Exception):
        parse_callback_data("bad")


def test_callback_parse_invalid_action() -> None:
    with pytest.raises(Exception):
        parse_callback_data("hack|draft-1234|content-1234")
