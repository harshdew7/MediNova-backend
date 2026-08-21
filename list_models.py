from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print("Available models:\n")

for model in client.models.list():
    print(model.name)