from types import SimpleNamespace

from onlycuts.app.services.operator_cycle_service import OperatorCycleService


class StubChannels:
    def __init__(self, channel):
        self.channel = channel

    def get_by_code(self, _code):
        return self.channel


class StubContentItems:
    def __init__(self, planned):
        self.planned = planned

    def list_by_status(self, status: str):
        if status == "planned":
            return self.planned
        return []


class StubDrafts:
    def __init__(self, pending):
        self.pending = pending

    def list_by_review_status(self, review_status: str):
        if review_status == "pending_review":
            return self.pending
        return []


class StubPlanner:
    def __init__(self, count=0):
        self.count = count

    def plan(self, _channel_id: str) -> int:
        return self.count


class StubDrafting:
    def __init__(self):
        self.calls = []

    def generate(self, content_item_id: str):
        self.calls.append(content_item_id)


class StubReview:
    def __init__(self):
        self.calls = []

    def review(self, draft_id: str):
        self.calls.append(draft_id)
        return True


class StubDispatch:
    def __init__(self, count: int):
        self.count = count

    def dispatch_pending_reviewed(self, channel_code: str | None = None) -> int:
        assert channel_code == "OnlyAiOps"
        return self.count


def test_operator_cycle_handles_empty_state() -> None:
    channel = SimpleNamespace(id="ch-1")
    service = OperatorCycleService(
        channels=StubChannels(channel),
        content_items=StubContentItems([]),
        drafts=StubDrafts([]),
        planner=StubPlanner(count=0),
        drafting=StubDrafting(),
        review=StubReview(),
        dispatch=StubDispatch(count=0),
    )

    summary = service.run("OnlyAiOps")
    assert summary.to_dict() == {"planned": 0, "drafted": 0, "reviewed": 0, "dispatched": 0}


def test_operator_cycle_runs_full_stages() -> None:
    channel = SimpleNamespace(id="ch-1")
    planned_item = SimpleNamespace(id="item-1", channel_id="ch-1")
    pending_draft = SimpleNamespace(id="draft-1")
    drafting = StubDrafting()
    review = StubReview()

    service = OperatorCycleService(
        channels=StubChannels(channel),
        content_items=StubContentItems([planned_item]),
        drafts=StubDrafts([pending_draft]),
        planner=StubPlanner(count=1),
        drafting=drafting,
        review=review,
        dispatch=StubDispatch(count=1),
    )

    summary = service.run("OnlyAiOps")
    assert summary.planned == 1
    assert summary.drafted == 1
    assert summary.reviewed == 1
    assert summary.dispatched == 1
    assert drafting.calls == ["item-1"]
    assert review.calls == ["draft-1"]
