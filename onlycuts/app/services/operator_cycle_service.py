from dataclasses import asdict, dataclass
from typing import Protocol


class ChannelsRepo(Protocol):
    def get_by_code(self, code: str): ...


class ContentItemsRepo(Protocol):
    def list_by_status(self, status: str): ...


class DraftsRepo(Protocol):
    def list_by_review_status(self, review_status: str): ...


@dataclass
class OperatorCycleSummary:
    planned: int = 0
    drafted: int = 0
    reviewed: int = 0
    dispatched: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


class OperatorCycleService:
    """Thin orchestrator for the local operator cycle."""

    def __init__(
        self,
        channels: ChannelsRepo,
        content_items: ContentItemsRepo,
        drafts: DraftsRepo,
        planner,
        drafting,
        review,
        dispatch,
    ):
        self.channels = channels
        self.content_items = content_items
        self.drafts = drafts
        self.planner = planner
        self.drafting = drafting
        self.review = review
        self.dispatch = dispatch

    def run(self, channel_code: str) -> OperatorCycleSummary:
        channel = self.channels.get_by_code(channel_code)
        if channel is None:
            raise ValueError(f"channel not found: {channel_code}")

        summary = OperatorCycleSummary()
        summary.planned = self.planner.plan(str(channel.id))

        planned_items = self.content_items.list_by_status("planned")
        for item in planned_items:
            if str(item.channel_id) != str(channel.id):
                continue
            self.drafting.generate(str(item.id))
            summary.drafted += 1

        pending_reviews = self.drafts.list_by_review_status("pending_review")
        for draft in pending_reviews:
            self.review.review(str(draft.id))
            summary.reviewed += 1

        summary.dispatched = self.dispatch.dispatch_pending_reviewed()
        return summary
