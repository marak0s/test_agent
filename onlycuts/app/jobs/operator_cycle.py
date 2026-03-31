from sqlalchemy.orm import Session

from onlycuts.app.integrations.telegram.bot_client import TelegramBotClient
from onlycuts.app.jobs.common import run_job
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.repositories.topics import TopicRepository
from onlycuts.app.services.approvals.approval_dispatch_service import ApprovalDispatchService
from onlycuts.app.services.drafting.draft_service import DraftGenerationService
from onlycuts.app.services.drafting.review_service import DraftReviewService
from onlycuts.app.services.operator_cycle_service import OperatorCycleService
from onlycuts.app.services.topics.planner_service import TopicPlannerService


def operator_cycle_job(session: Session, channel_code: str) -> dict:
    channels = ChannelRepository(session)
    content_items = ContentItemRepository(session)
    drafts = DraftRepository(session)
    artifacts = ArtifactRepository(session)
    topics = TopicRepository(session)

    service = OperatorCycleService(
        channels=channels,
        content_items=content_items,
        drafts=drafts,
        planner=TopicPlannerService(topics=topics, content_items=content_items, artifacts=artifacts),
        drafting=DraftGenerationService(content_items=content_items, drafts=drafts, artifacts=artifacts, channels=channels),
        review=DraftReviewService(drafts=drafts, artifacts=artifacts),
        dispatch=ApprovalDispatchService(
            bot=TelegramBotClient(),
            artifacts=artifacts,
            drafts=drafts,
            content_items=content_items,
            topics=topics,
            channels=channels,
        ),
    )

    return run_job(
        session=session,
        name="operator_cycle",
        payload={"channel_code": channel_code},
        fn=lambda: service.run(channel_code).to_dict(),
    )
