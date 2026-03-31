class GeminiClient:
    def generate(self, prompt: str) -> dict:
        return {"provider": "gemini", "text": prompt[:100], "note": "TODO integrate real API"}
