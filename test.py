import os
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

# Gemini Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("===== AVAILABLE MODELS =====\n")

try:
    for model in client.models.list():
        print(model.name)

except Exception as e:
    print("\nERROR:")
    print(e)