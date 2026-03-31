from sqlalchemy.orm import Session

from onlycuts.app.integrations.telegram.bot_client import TelegramBotClient
from onlycuts.app.jobs.common import run_job
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.repositories.topics import TopicRepository
from onlycuts.app.services.approvals.approval_dispatch_service import ApprovalDispatchService


def approval_dispatch_job(session: Session) -> dict:
    service = ApprovalDispatchService(
        bot=TelegramBotClient(),
        artifacts=ArtifactRepository(session),
        drafts=DraftRepository(session),
        content_items=ContentItemRepository(session),
        topics=TopicRepository(session),
    )

    return run_job(
        session=session,
        name="approval_dispatch",
        payload={},
        fn=lambda: {"dispatched": service.dispatch_pending_reviewed()},
    )
