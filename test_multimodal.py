"""
Live compatibility test for google-genai 2.x typed multimodal content.

Run:

    python test_multimodal.py
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ----------------------------------------------------
# Project paths
# ----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"

TEST_PNG = (
    PROJECT_ROOT
    / "output"
    / "crops"
    / "135c97572a9bdfb6"
    / "Q1.png"
)

# ----------------------------------------------------
# Load .env
# ----------------------------------------------------

print("=" * 60)
print("PROJECT ROOT :", PROJECT_ROOT)
print(".env PATH    :", ENV_FILE)
print(".env EXISTS  :", ENV_FILE.exists())

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY")

print("API KEY LOADED :", bool(API_KEY))
print("KEY LENGTH     :", len(API_KEY) if API_KEY else 0)
print("=" * 60)

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY was not loaded.")

# ----------------------------------------------------
# Check image
# ----------------------------------------------------

if not TEST_PNG.exists():
    raise FileNotFoundError(f"Image not found:\n{TEST_PNG}")

print("IMAGE :", TEST_PNG)
print("SIZE  :", TEST_PNG.stat().st_size, "bytes")

# ----------------------------------------------------
# Build typed request
# ----------------------------------------------------

contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text="""
Describe this questionnaire crop.

Return ONLY this JSON:

{
  "status":"received"
}
"""
            ),
            types.Part.from_bytes(
                data=TEST_PNG.read_bytes(),
                mime_type="image/png",
            ),
        ],
    )
]

# ----------------------------------------------------
# Gemini
# ----------------------------------------------------

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="models/gemini-3.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        temperature=0,
        response_mime_type="application/json",
    ),
)

print("\n")
print("=" * 60)
print("TEXT")
print("=" * 60)
print(response.text)

print("\n")
print("=" * 60)
print("MODEL DUMP")
print("=" * 60)

try:
    print(response.model_dump())
except Exception:
    print(response)