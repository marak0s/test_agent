from onlycuts.app.domain.enums.statuses import ContentStatus, TopicStatus
from onlycuts.app.llm.prompts.planner_prompt import build_planner_prompt
from onlycuts.app.llm.schemas.planner_output import PlannerOutput
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.topics import TopicRepository


class TopicPlannerService:
    def __init__(self, topics: TopicRepository, content_items: ContentItemRepository, artifacts: ArtifactRepository):
        self.topics = topics
        self.content_items = content_items
        self.artifacts = artifacts

    def plan(self, channel_id: str) -> int:
        planned = 0
        for topic in self.topics.list_new(channel_id):
            prompt = build_planner_prompt(topic.title)
            output = PlannerOutput(
                recommended_rubric="insight",
                angle="operator lessons",
                fit_score=0.8,
                novelty_score=0.7,
                business_value_score=0.75,
                concise_brief=prompt,
            )
            self.content_items.get_or_create(channel_id=topic.channel_id, topic_id=topic.id, goal=output.angle, status=ContentStatus.PLANNED.value)
            topic.status = TopicStatus.PLANNED.value
            self.artifacts.create(kind="planner_output", ref_id=str(topic.id), payload=output.model_dump())
            planned += 1
        return planned
