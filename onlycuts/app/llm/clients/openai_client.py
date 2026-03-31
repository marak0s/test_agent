from openai import OpenAI
from onlycuts.app.config.settings import settings

class OpenAIClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, prompt: str, model: str, tools: list[str] | None = None) -> dict:
        tool_defs = []
        if tools and "web_search" in tools:
            tool_defs.append({"type": "web_search"})

        response = self.client.responses.create(
            model=model,
            input=prompt,
            tools=tool_defs or None,
        )

        return {
            "provider": "openai",
            "model": model,
            "text": response.output_text,
            "response_id": response.id,
        }