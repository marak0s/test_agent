class AnthropicClient:
    def generate(self, prompt: str) -> dict:
        return {"provider": "anthropic", "text": prompt[:100], "note": "TODO integrate real API"}
