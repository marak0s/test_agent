class OpenAIClient:
    def generate(self, prompt: str) -> dict:
        return {"provider": "openai", "text": prompt[:100], "note": "TODO integrate real API"}
