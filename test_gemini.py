from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="models/gemini-3.5-flash",
    contents="Reply with exactly the word OK"
)

print("TEXT:")
print(repr(response.text))

print("\nFULL RESPONSE:")
try:
    print(response.model_dump())
except Exception:
    print(response)