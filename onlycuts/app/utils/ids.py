from uuid import uuid4


def short_id(value: str) -> str:
    return value.split("-")[0]


def new_uuid() -> str:
    return str(uuid4())
