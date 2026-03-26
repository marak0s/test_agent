def redact_secrets(value: str) -> str:
    return value.replace("token", "[redacted]")
