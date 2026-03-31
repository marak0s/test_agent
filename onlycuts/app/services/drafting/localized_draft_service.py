from __future__ import annotations

from onlycuts.app.domain.enums.statuses import DraftReviewStatus
from onlycuts.app.llm.clients.openai_client import OpenAIClient
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository


class LocalizedDraftService:
    def __init__(
        self,
        content_items: ContentItemRepository,
        drafts: DraftRepository,
        artifacts: ArtifactRepository,
        channels: ChannelRepository,
        llm_client: OpenAIClient,
    ):
        self.content_items = content_items
        self.drafts = drafts
        self.artifacts = artifacts
        self.channels = channels
        self.llm_client = llm_client

    def generate(self, source_draft_id: str, target_content_item_id: str) -> str:
        source_draft = self.drafts.get(source_draft_id)
        if source_draft is None:
            raise ValueError("source draft not found")

        target_item = self.content_items.get(target_content_item_id)
        if target_item is None:
            raise ValueError("target content item not found")

        channel = self.channels.get(str(target_item.channel_id))
        target_language = channel.language if channel is not None else "en"
        target_locale = channel.locale if channel is not None else "en_US"

        prompt = self._build_prompt(
            source_text=source_draft.body_text,
            target_language=target_language,
            target_locale=target_locale,
            target_goal=target_item.goal,
        )
        result = self.llm_client.generate(prompt)
        localized_text = self._clean_output(result.get("text", ""))
        if not localized_text:
            raise ValueError("localized draft output is empty")

        target_draft = self.drafts.create(
            content_item_id=str(target_item.id),
            channel_id=str(target_item.channel_id),
            body_text=localized_text,
            review_status=DraftReviewStatus.PENDING_REVIEW.value,
        )
        target_item.current_draft_id = target_draft.id
        target_item.status = "review"

        self.artifacts.create(
            kind="localized_draft_output",
            ref_id=str(target_draft.id),
            payload={
                "source_draft_id": str(source_draft.id),
                "target_content_item_id": str(target_item.id),
                "target_language": target_language,
                "target_locale": target_locale,
                "body_text": localized_text,
                "provider_output": result,
            },
        )
        return str(target_draft.id)

    def _build_prompt(self, source_text: str, target_language: str, target_locale: str, target_goal: str) -> str:
        return (
            "You are localizing a Telegram post draft.\n"
            "Preserve core meaning, hook, and CTA from source.\n"
            "Do not add fabricated claims or new facts.\n"
            "Output only final post text, no labels.\n\n"
            f"Target language: {target_language}\n"
            f"Target locale: {target_locale}\n"
            f"Target goal: {target_goal}\n\n"
            "Source draft:\n"
            f"{source_text}"
        )

    def _clean_output(self, value: str) -> str:
        cleaned_lines: list[str] = []
        for raw_line in value.strip().splitlines():
            line = raw_line.strip()
            lowered = line.lower()
            if lowered.startswith("language:") or lowered.startswith("goal:") or lowered.startswith("draft:"):
                continue
            if not line and (not cleaned_lines or cleaned_lines[-1] == ""):
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()
