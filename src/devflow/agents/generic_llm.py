"""Generic LLM agent that works with any OpenAI-compatible API.

Supports:
- OpenAI API
- Anthropic API (via compatibility layer)
- Any OpenAI-compatible API (GLM, DeepSeek, etc.)
"""

import os
from typing import Any, Dict, List, Optional

import httpx


class GenericLLMAgent:
    """Generic LLM agent for OpenAI-compatible APIs."""

    def __init__(
        self,
        model: str,
        system_prompt: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize generic LLM agent.

        Args:
            model: Model name (e.g., "gpt-4", "glm5.3-flash")
            system_prompt: System prompt for the agent
            api_key: API key (defaults to LLM_API_KEY env var)
            base_url: Base URL (defaults to LLM_BASE_URL or OpenAI)
        """
        self.model = model
        self.system_prompt = system_prompt
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv(
            "LLM_BASE_URL", "https://api.openai.com/v1"
        )

        if not self.api_key:
            raise ValueError(
                "API key required. Set LLM_API_KEY environment variable or pass api_key parameter."
            )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        """Generate response using OpenAI-compatible API.

        Args:
            prompt: User prompt
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        """Generate JSON response.

        Args:
            prompt: User prompt (should request JSON output)
            temperature: Temperature
            max_tokens: Maximum tokens

        Returns:
            Generated JSON string
        """
        # Some APIs support response_format, others don't
        # Try with response_format first, fall back to regular
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Try with response_format for JSON mode
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except (httpx.HTTPStatusError, KeyError):
                # Fallback: regular generation (hope it returns JSON)
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
