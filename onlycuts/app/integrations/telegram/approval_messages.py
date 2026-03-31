from onlycuts.app.utils.ids import short_id

ACTIONS = ["post", "regen", "shorter", "stronger", "reject", "queue", "help"]


def build_approval_message(
    topic_title: str,
    content_item_id: str,
    draft_id: str,
    goal: str,
    body_text: str,
    review_summary: str | None = None,
) -> str:
    summary = f"\nReview: {review_summary}" if review_summary else ""
    return (
        f"Rubric: Quality / Novelty / Risk\n"
        f"Topic: {topic_title}\n"
        f"Content: {short_id(content_item_id)}\n"
        f"Draft: {short_id(draft_id)}\n"
        f"Goal: {goal}\n\n"
        f"{body_text}{summary}\n\n"
        f"Actions: {', '.join(ACTIONS)}\n"
        f"Reply with one command above to approve/rewrite.\n"
        f"RefDraft: {draft_id}\n"
        f"RefContent: {content_item_id}"
    )


def inline_keyboard(draft_id: str, content_item_id: str) -> dict:
    return {
        "inline_keyboard": [
            [{"text": a, "callback_data": a} for a in ACTIONS if a != "help"]
        ]
    }