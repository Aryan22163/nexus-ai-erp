import logging
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("nexus.ai.llm")


class OpenSourceLLMClient:
    """
    Client for Open-Source Large Language Models (LLMs).
    Supports:
      - Ollama (Llama 3.1, Llama 3.2, DeepSeek-R1, Mistral, Qwen 2.5) via standard OpenAI-compatible API
      - Local inference servers: vLLM, LocalAI, LM Studio, Jan
      - Cloud-hosted open models: Groq (Llama 3.1, Mixtral), Together AI, HuggingFace Inference
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = (base_url or settings.LOCAL_LLM_BASE_URL).rstrip("/")
        self.model = model or settings.LOCAL_LLM_MODEL
        self.timeout = timeout

    async def is_available(self) -> bool:
        """Check if local open-source LLM server (e.g. Ollama) is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                # Check root or models list
                resp = await client.get(f"{self.base_url}/models")
                if resp.status_code in (200, 404):
                    return True
                # Check native Ollama root if base_url ends in /v1
                native_url = self.base_url.replace("/v1", "")
                resp_native = await client.get(native_url)
                return resp_native.status_code == 200
        except Exception:
            return False

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """
        Send a chat completion request to the open-source LLM endpoint.
        Returns the text response or None if the server is unreachable.
        """
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": payload_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {"Content-Type": "application/json"}
                # If using Groq or custom bearer token for open-source models
                if hasattr(settings, "GROQ_API_KEY") and settings.GROQ_API_KEY:
                    headers["Authorization"] = f"Bearer {settings.GROQ_API_KEY}"

                resp = await client.post(endpoint, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        return choices[0]["message"].get("content", "").strip()
                else:
                    logger.warning(
                        f"OpenSourceLLM returned status {resp.status_code}: {resp.text}"
                    )
        except httpx.ConnectError:
            logger.info(f"OpenSource LLM at {self.base_url} is not running.")
        except Exception as exc:
            logger.error(f"Failed to query OpenSource LLM: {exc}")

        return None


# Global Open Source LLM client instance
open_source_llm = OpenSourceLLMClient()
