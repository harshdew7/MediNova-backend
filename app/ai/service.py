import json

from sqlalchemy.orm import Session

from google.genai.errors import ClientError, ServerError

from app.ai.gemini_provider import GeminiProvider
from app.models.user import User
from app.repositories.consultation_repository import ConsultationRepository
from app.schemas.ai import AIConsultResponse


class AIService:
    def __init__(self):
        self.provider = GeminiProvider()

    def consult(
        self,
        db: Session,
        user: User,
        message: str,
    ) -> AIConsultResponse:

        try:
            response = self.provider.generate_response(message)

            # Convert Gemini JSON string to dictionary
            data = json.loads(response)

            ai_response = AIConsultResponse(**data)

            # Save consultation
            repository = ConsultationRepository(db)

            repository.create(
                user_id=user.id,
                user_message=message,
                ai_response=ai_response.response,
                risk_level=ai_response.risk_level,
            )

            return ai_response

        except json.JSONDecodeError:
            return AIConsultResponse(
                response="The AI returned an invalid response.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )

        except ClientError as e:
            print(f"\nCLIENT ERROR:\n{e}\n")

            return AIConsultResponse(
                response="The AI service is temporarily unavailable due to quota limits.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )

        except ServerError as e:
            print(f"\nSERVER ERROR:\n{e}\n")

            return AIConsultResponse(
                response="The AI service is currently busy. Please try again in a few moments.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )

        except Exception as e:
            print(f"\nUNEXPECTED ERROR:\n{e}\n")

            return AIConsultResponse(
                response="An unexpected error occurred.",
                risk_level="unknown",
                show_emergency_button=False,
                emergency_number=None,
            )