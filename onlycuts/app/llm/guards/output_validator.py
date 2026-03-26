def ensure_nonempty(output: dict) -> None:
    if not output:
        raise ValueError("LLM output is empty")
