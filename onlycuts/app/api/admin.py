from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from onlycuts.app.config.settings import settings
from onlycuts.app.db.session import SessionLocal
from onlycuts.app.jobs.approval_dispatch import approval_dispatch_job
from onlycuts.app.jobs.operator_cycle import operator_cycle_job
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.topics import TopicRepository
from onlycuts.app.services.topics.fanout_service import TopicFanoutService

router = APIRouter(prefix="/admin")


class RunJobRequest(BaseModel):
    job_name: str
    channel_code: str | None = None
    topic_id: str | None = None
    channel_codes: list[str] | None = None


class RunJobResponse(BaseModel):
    accepted: bool
    output: dict | None = None


@router.post("/run-job", response_model=RunJobResponse)
def run_job(request: RunJobRequest) -> RunJobResponse:
    with SessionLocal() as session:
        if request.job_name == "approval_dispatch":
            output = approval_dispatch_job(session, channel_code=request.channel_code)
            return RunJobResponse(accepted=True, output=output)

        if request.job_name == "operator_cycle":
            channel_code = request.channel_code or settings.default_channel_code
            output = operator_cycle_job(session, channel_code=channel_code)
            return RunJobResponse(accepted=True, output=output)

        if request.job_name == "topic_fanout":
            if request.topic_id is None or not request.channel_codes:
                raise HTTPException(status_code=400, detail="topic_id and channel_codes are required")
            service = TopicFanoutService(
                topics=TopicRepository(session),
                channels=ChannelRepository(session),
                content_items=ContentItemRepository(session),
            )
            result = service.fan_out(topic_id=request.topic_id, channel_codes=request.channel_codes)
            session.commit()
            return RunJobResponse(accepted=True, output={"created": result.created, "skipped_existing": result.skipped_existing})

    raise HTTPException(status_code=400, detail="unsupported job_name")
