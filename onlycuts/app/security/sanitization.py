import re


def sanitize_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value
