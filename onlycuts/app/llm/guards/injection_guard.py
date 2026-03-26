def contains_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return "ignore previous instructions" in lowered or "system prompt" in lowered
