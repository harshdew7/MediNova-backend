from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

models = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

for model in models:
    print(f"\n{'=' * 60}")
    print(f"Testing: {model}")

    try:
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly one word: Hello"
        )

        print("✅ SUCCESS")
        print(response.text)

    except Exception as e:
        print(f"❌ {type(e).__name__}")
        print(e)