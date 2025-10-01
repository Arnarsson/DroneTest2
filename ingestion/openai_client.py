"""OpenAI client utilities for text cleanup."""

import logging
import os
from typing import Optional

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)


class OpenAIClientError(Exception):
    """Raised when the OpenAI API returns an error."""


class OpenAIClient:
    """Lightweight OpenAI client for text cleanup"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.model_name = model
        self.client = OpenAI(api_key=self.api_key)

    def cleanup_text(self, text: str, *, max_tokens: int = 512) -> str:
        """Call OpenAI to clean up noisy article text."""

        system_prompt = (
            "You clean up scraped news article content. Remove leftover text from "
            "news website UI elements like 'play-circle', 'Læs op', navigation menus, "
            "advertisements, social media buttons, and other non-article content. "
            " Preserve only the factual news content in Danish or English. "
            "Do NOT rewrite or rephrase anything - keep the original content exactly as written after cleaning. "
            "Return clean, readable text only."
        )

        try:
            completion_params = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            }

            response = self.client.chat.completions.create(**completion_params)
        except OpenAIError as exc:
            logger.error("OpenAI cleanup failed: %s", exc, exc_info=True)
            raise OpenAIClientError("OpenAI cleanup failed") from exc

        if not response or not response.choices:
            logger.warning(
                "OpenAI cleanup returned no choices; fallback to original text")
            return text

        choice = response.choices[0]
        if not choice.message or not choice.message.content:
            logger.warning(
                "OpenAI cleanup returned empty content; fallback to original text")
            return text

        cleaned = choice.message.content.strip()

        if not cleaned:
            logger.warning(
                "OpenAI cleanup returned blank text; fallback to original")
            return text

        return cleaned
