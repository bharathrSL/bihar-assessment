"""Minimal OpenRouter client shared by the questionnaire extraction provider."""
from __future__ import annotations

import logging
import os
import time
import csv
from pathlib import Path
from datetime import datetime

import httpx
from core.analytics.pricing import calculate_cost

logger = logging.getLogger(__name__)
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-3.5-flash")


def get_tokens_from_env(prefix: str) -> list[str]:
    tokens: list[str] = []
    if os.getenv(f"{prefix}_API_KEY"):
        tokens.append(os.environ[f"{prefix}_API_KEY"])
    index = 1
    while os.getenv(f"{prefix}_TOKEN{index}"):
        tokens.append(os.environ[f"{prefix}_TOKEN{index}"])
        index += 1
    if not tokens and os.getenv(f"{prefix}_TOKEN"):
        tokens.append(os.environ[f"{prefix}_TOKEN"])
    return tokens


class UsageMetadata:
    def __init__(self, prompt_tokens: int = 0, candidates_tokens: int = 0, total_tokens: int = 0):
        self.prompt_token_count = prompt_tokens
        self.candidates_token_count = candidates_tokens
        self.total_token_count = total_tokens


class ProviderResponse:
    def __init__(self, text: str, usage_metadata: UsageMetadata | None = None):
        self.text = text
        self.usage_metadata = usage_metadata or UsageMetadata()


class LLMClient:
    """OpenRouter chat-completions client with optional API-key rotation."""

    def __init__(self, model_name: str | None = None, **_unused: object):
        self.model_name = model_name or os.getenv("OPENROUTER_MODEL", OPENROUTER_MODEL)
        self.tokens = get_tokens_from_env("OPENROUTER")
        self.current_token_index = 0
        self.active_token = self.get_active_token()

    def get_active_token(self) -> str | None:
        return self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else None

    def switch_to_next_token(self) -> bool:
        self.current_token_index += 1
        self.active_token = self.get_active_token()
        return self.active_token is not None

    def generate_content(self, contents: list[object] | str, max_retries: int = 3) -> ProviderResponse:
        if not self.active_token:
            raise ValueError("OpenRouter API token not found in environment")
        start_time = time.time()
        user_content: list[dict] = []
        source = [contents] if isinstance(contents, str) else contents
        for item in source:
            if isinstance(item, str):
                user_content.append({"type": "text", "text": item})
            elif isinstance(item, dict) and "data" in item:
                mime_type = str(item.get("mime_type", ""))
                if not mime_type.startswith("image/"):
                    raise ValueError(f"Unsupported binary data: {mime_type}")
                user_content.append({"type": "image_url", "image_url": {
                    "url": f"data:{mime_type};base64,{item['data']}"}})
            else:
                raise ValueError("OpenRouter content must be text or an image data object")

        for attempt in range(max_retries):
            response = None
            headers = {
                "Authorization": f"Bearer {self.active_token}",
                "Content-Type": "application/json",
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "Bihar Assessment"),
            }
            if os.getenv("OPENROUTER_SITE_URL"):
                headers["HTTP-Referer"] = os.environ["OPENROUTER_SITE_URL"]
            payload = {"model": self.model_name, "messages": [{"role": "user", "content": user_content}], "temperature": 0}
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if not text:
                    raise ValueError(f"OpenRouter response contains no message content: {data}")
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                latency = round(time.time() - start_time, 3)

                cost = calculate_cost(
                    self.model_name,
                    prompt_tokens,
                    completion_tokens,
                )

                log_file = Path("results") / "api_usage_log.csv"

                file_exists = log_file.exists()

                with open(log_file, "a", newline="", encoding="utf-8") as f:

                    writer = csv.writer(f)

                    if not file_exists:
                        writer.writerow([
                            "Timestamp",
                            "Model_Name",
                            "Input_Tokens",
                            "Output_Tokens",
                            "Total_Tokens",
                            "Latency_Seconds",
                            "Total_Cost_USD",
                            "Status",
                        ])

                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        self.model_name,
                        prompt_tokens,
                        completion_tokens,
                        total_tokens,
                        latency,
                        cost,
                        "success",
                    ])
                return ProviderResponse(text, UsageMetadata(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), usage.get("total_tokens", 0)))
            except Exception as error:
                if response is not None and response.status_code == 429 and self.switch_to_next_token():
                    logger.warning("OpenRouter rate limited; switching API token")
                    continue
                if attempt == max_retries - 1:
                    log_file = Path("results") / "api_usage_log.csv"
                    
                    file_exists = log_file.exists()
                    
                    with open(log_file, "a", newline="", encoding="utf-8") as f:
                    
                        writer = csv.writer(f)
                    
                        if not file_exists:
                            writer.writerow([
                                "Timestamp",
                                "Model_Name",
                                "Input_Tokens",
                                "Output_Tokens",
                                "Total_Tokens",
                                "Latency_Seconds",
                                "Total_Cost_USD",
                                "Status",
                            ])
                    
                        writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            self.model_name,
                            0,
                            0,
                            0,
                            round(time.time() - start_time, 3),
                            0,
                            "failure",
                        ])
                    raise RuntimeError(f"OpenRouter request failed: {error}") from error
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError("OpenRouter request failed after retries")
