import pytest

from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data


def test_callback_parse_success() -> None:
    parsed = parse_callback_data("post|draft-1|content-1")
    assert parsed.action == "post"


def test_callback_parse_invalid() -> None:
    with pytest.raises(Exception):
        parse_callback_data("bad")
