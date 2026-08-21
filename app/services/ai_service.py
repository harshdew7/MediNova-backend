import json

from google.genai.errors import ClientError, ServerError

from app.ai.gemini_provider import GeminiProvider
from app.core.logger import logger
from app.schemas.ai import AIConsultResponse


class AIService:
    def __init__(self):
        self.provider = GeminiProvider()

    def consult(self, message: str) -> AIConsultResponse:
        logger.info("AI consultation started.")

        try:
            response = self.provider.generate_response(message)

            logger.info("Gemini response received successfully.")

            data = json.loads(response)

            logger.info(
                "AI consultation completed successfully. Risk Level: %s",
                data.get("risk_level"),
            )

            return AIConsultResponse(**data)

        except json.JSONDecodeError:
            logger.exception("Failed to parse Gemini JSON response.")

            return AIConsultResponse(
                response="The AI returned an invalid response.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )

        except ClientError:
            logger.exception("Gemini Client Error")

            return AIConsultResponse(
                response="The AI service is temporarily unavailable due to quota limits. Please try again later.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )

        except ServerError:
            logger.exception("Gemini Server Error")

            return AIConsultResponse(
                response="The AI service is currently busy. Please try again in a few moments.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )

        except Exception:
            logger.exception("Unexpected AI Service Error")

            return AIConsultResponse(
                response="An unexpected error occurred while processing your consultation.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )