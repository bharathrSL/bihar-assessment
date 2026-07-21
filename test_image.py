from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

with open("reference_pages/page_1.png","rb") as f:
    img = f.read()

response = client.models.generate_content(
    model="models/gemini-3.5-flash",
    contents=[
        "What is shown in this image?",
        {
            "mime_type":"image/png",
            "data":img
        }
    ]
)

print(response.text)