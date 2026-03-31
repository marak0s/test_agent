import argparse

from onlycuts.app.db.session import SessionLocal
from onlycuts.app.llm.clients.openai_client import OpenAIClient
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.services.drafting.localized_draft_service import LocalizedDraftService


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate localized draft from a source draft")
    parser.add_argument("--source-draft", required=True)
    parser.add_argument("--target-content-item", required=True)
    args = parser.parse_args()

    with SessionLocal() as session:
        service = LocalizedDraftService(
            content_items=ContentItemRepository(session),
            drafts=DraftRepository(session),
            artifacts=ArtifactRepository(session),
            channels=ChannelRepository(session),
            llm_client=OpenAIClient(),
        )
        draft_id = service.generate(
            source_draft_id=args.source_draft,
            target_content_item_id=args.target_content_item,
        )
        session.commit()
        print(draft_id)
