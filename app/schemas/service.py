from app.ai.gemini_provider import GeminiProvider


class AIService:
    def __init__(self):
        self.provider = GeminiProvider()

    def consult(self, message: str) -> str:
        return self.provider.generate_response(message)