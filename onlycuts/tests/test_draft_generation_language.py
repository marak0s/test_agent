from types import SimpleNamespace

from onlycuts.app.services.drafting.draft_service import DraftGenerationService


class StubContentRepo:
    def get(self, content_item_id: str):
        return SimpleNamespace(id=content_item_id, goal="Goal", channel_id="ch-ru")


class StubDraftRepo:
    def create(self, **kwargs):
        return SimpleNamespace(id="draft-1", **kwargs)


class StubArtifacts:
    def __init__(self):
        self.payload = None

    def create(self, kind: str, ref_id: str, payload: dict):
        self.payload = payload
        return SimpleNamespace(kind=kind, ref_id=ref_id)


class StubChannels:
    def get(self, channel_id: str):
        assert channel_id == "ch-ru"
        return SimpleNamespace(language="ru", locale="ru_RU")


def test_draft_generation_includes_channel_language_context() -> None:
    artifacts = StubArtifacts()
    service = DraftGenerationService(
        content_items=StubContentRepo(),
        drafts=StubDraftRepo(),
        artifacts=artifacts,
        channels=StubChannels(),
    )

    service.generate("content-1")
    assert "Language: ru" in artifacts.payload["body_text"]
