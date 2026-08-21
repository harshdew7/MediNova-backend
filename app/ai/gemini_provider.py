from google import genai

from app.ai.base_provider import BaseAIProvider
from app.ai.prompts import SYSTEM_PROMPT
from app.core.config import settings


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_response(self, message: str) -> str:
        prompt = f"""
{SYSTEM_PROMPT}

User:
{message}
"""

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text