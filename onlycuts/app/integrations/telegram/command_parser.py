from dataclasses import dataclass

from onlycuts.app.integrations.telegram.approval_messages import ACTIONS


@dataclass(frozen=True)
class ParsedCommand:
    action: str
    modifier: str | None = None
    queue_note: str | None = None


def parse_approval_command(text: str) -> ParsedCommand:
    clean = " ".join(text.strip().lower().split())
    if not clean:
        raise ValueError("empty command")

    parts = clean.split(" ")
    action = parts[0]
    if action not in ACTIONS:
        raise ValueError("unsupported command")

    if action == "regen":
        modifier = parts[1] if len(parts) > 1 and parts[1] in {"stronger", "shorter"} else None
        return ParsedCommand(action="regen", modifier=modifier)

    if action == "queue":
        return ParsedCommand(action="queue", queue_note=clean[len("queue") :].strip() or None)

    return ParsedCommand(action=action)


def extract_ids_from_approval_message(text: str) -> tuple[str, str]:
    draft_id = ""
    content_item_id = ""
    for line in text.splitlines():
        if line.startswith("RefDraft:"):
            draft_id = line.split(":", maxsplit=1)[1].strip()
        if line.startswith("RefContent:"):
            content_item_id = line.split(":", maxsplit=1)[1].strip()
    if not draft_id or not content_item_id:
        raise ValueError("approval message refs not found")
    return draft_id, content_item_id
