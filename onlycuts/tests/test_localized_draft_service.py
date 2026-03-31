from types import SimpleNamespace

from onlycuts.app.services.drafting.localized_draft_service import LocalizedDraftService


class StubContentRepo:
    def __init__(self):
        self.items = {
            "target-item": SimpleNamespace(id="target-item", channel_id="ch-ru", goal="Drive engagement", status="planned")
        }

    def get(self, content_item_id: str):
        return self.items.get(content_item_id)


class StubDraftRepo:
    def __init__(self):
        self.source = SimpleNamespace(id="source-draft", body_text="Original EN post with CTA")
        self.created = []

    def get(self, draft_id: str):
        if draft_id == "source-draft":
            return self.source
        for draft in self.created:
            if draft.id == draft_id:
                return draft
        return None

    def create(self, **kwargs):
        draft = SimpleNamespace(id=f"localized-{len(self.created) + 1}", **kwargs)
        self.created.append(draft)
        return draft


class StubArtifacts:
    def __init__(self):
        self.records = []

    def create(self, kind: str, ref_id: str, payload: dict):
        self.records.append(SimpleNamespace(kind=kind, ref_id=ref_id, payload=payload))


class StubChannels:
    def get(self, channel_id: str):
        assert channel_id == "ch-ru"
        return SimpleNamespace(language="ru", locale="ru_RU")


class StubOpenAI:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str):
        self.prompts.append(prompt)
        return {"text": "Language: ru\nGoal: Drive engagement\n\nЛокализованный пост.\nCTA в конце."}


def test_localized_draft_creates_new_target_draft() -> None:
    content = StubContentRepo()
    drafts = StubDraftRepo()
    artifacts = StubArtifacts()
    llm = StubOpenAI()
    service = LocalizedDraftService(content, drafts, artifacts, StubChannels(), llm)

    localized_id = service.generate(source_draft_id="source-draft", target_content_item_id="target-item")

    assert localized_id == "localized-1"
    assert drafts.source.body_text == "Original EN post with CTA"
    assert content.items["target-item"].current_draft_id == "localized-1"
    assert content.items["target-item"].status == "review"
    assert drafts.created[0].body_text == "Локализованный пост.\nCTA в конце."


def test_localized_draft_uses_target_channel_language_and_locale() -> None:
    content = StubContentRepo()
    drafts = StubDraftRepo()
    artifacts = StubArtifacts()
    llm = StubOpenAI()
    service = LocalizedDraftService(content, drafts, artifacts, StubChannels(), llm)

    service.generate(source_draft_id="source-draft", target_content_item_id="target-item")

    assert "Target language: ru" in llm.prompts[0]
    assert "Target locale: ru_RU" in llm.prompts[0]


def test_localized_draft_stores_artifact_payload() -> None:
    content = StubContentRepo()
    drafts = StubDraftRepo()
    artifacts = StubArtifacts()
    llm = StubOpenAI()
    service = LocalizedDraftService(content, drafts, artifacts, StubChannels(), llm)

    service.generate(source_draft_id="source-draft", target_content_item_id="target-item")

    assert artifacts.records[0].kind == "localized_draft_output"
    assert artifacts.records[0].payload["source_draft_id"] == "source-draft"
    assert artifacts.records[0].payload["target_language"] == "ru"


def test_localized_draft_allows_repeat_generation_for_same_target_item() -> None:
    content = StubContentRepo()
    drafts = StubDraftRepo()
    artifacts = StubArtifacts()
    llm = StubOpenAI()
    service = LocalizedDraftService(content, drafts, artifacts, StubChannels(), llm)

    first = service.generate(source_draft_id="source-draft", target_content_item_id="target-item")
    second = service.generate(source_draft_id="source-draft", target_content_item_id="target-item")

    assert first == "localized-1"
    assert second == "localized-2"
    assert len(drafts.created) == 2
