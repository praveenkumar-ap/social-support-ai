import os
import logging
import requests
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Wraps the Ollama HTTP API (OpenWebUI-compatible) at /api/chat/completions.
    Reads model name and timeouts from environment.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL")
        if not self.model:
            raise RuntimeError("OLLAMA_MODEL must be set in the environment")

        # Connect/read timeouts for requests
        try:
            self.timeout_connect = float(os.getenv("CHATBOT_CONNECT_TIMEOUT", "3"))
            self.timeout_read = float(os.getenv("CHATBOT_READ_TIMEOUT", "30"))
        except ValueError:
            logger.warning("Invalid CHATBOT_*_TIMEOUT; defaulting to 3/30s")
            self.timeout_connect = 3.0
            self.timeout_read = 30.0

    def chat(self, user_id: str, messages: list[str], context: dict):
        """
        Send a single‐shot chat completion request (no streaming) to Ollama.
        Returns ([response_text], session_id).
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": m} for m in messages],
            "stream": False,
        }

        try:
            resp = requests.post(
                url,
                json=payload,
                timeout=(self.timeout_connect, self.timeout_read),
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ LLM connect error: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to connect to LLM host",
            )
        except requests.exceptions.ReadTimeout as e:
            logger.error(f"❌ LLM read timeout: {e}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM host read timeout",
            )
        except requests.exceptions.HTTPError as e:
            text = getattr(resp, "text", "")
            logger.error(f"❌ LLM error {resp.status_code}: {text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LLM host error: {resp.status_code}",
            )

        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
            session_id = data.get("id", "")
        except (KeyError, IndexError):
            logger.error("❌ Unexpected LLM response format")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unexpected LLM response format",
            )

        return [content], session_id