def truncate(value: str, max_len: int = 250) -> str:
    return value if len(value) <= max_len else value[: max_len - 3] + "..."
