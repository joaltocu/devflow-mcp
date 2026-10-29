"""Claude API agent base class for custom agents."""

import os
from typing import Any, Dict, Optional

import anthropic
from anthropic import AsyncAnthropic


class ClaudeAPIAgent:
    """Base class for custom agents using Claude API."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-5-20250929",
        system_prompt: str = "",
        max_tokens: int = 4096,
    ) -> None:
        """Initialize Claude API agent.

        Args:
            model: Claude model to use
            system_prompt: System prompt for the agent
            max_tokens: Maximum tokens for response
        """
        self.model = model
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = AsyncAnthropic(api_key=api_key)
        self.total_tokens_used = 0

    async def run(
        self,
        user_prompt: str,
        system_prompt_override: Optional[str] = None,
    ) -> str:
        """Run the agent with a user prompt.

        Args:
            user_prompt: User prompt to send to the agent
            system_prompt_override: Optional override for system prompt

        Returns:
            Agent response text
        """
        system_prompt = system_prompt_override or self.system_prompt

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )

            # Track token usage
            self.total_tokens_used += response.usage.input_tokens
            self.total_tokens_used += response.usage.output_tokens

            # Extract text from response
            if response.content:
                return response.content[0].text

            return ""

        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {str(e)}") from e

    async def run_with_retries(
        self,
        user_prompt: str,
        max_retries: int = 3,
        system_prompt_override: Optional[str] = None,
    ) -> str:
        """Run the agent with automatic retries on failure.

        Args:
            user_prompt: User prompt to send to the agent
            max_retries: Maximum number of retry attempts
            system_prompt_override: Optional override for system prompt

        Returns:
            Agent response text
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.run(user_prompt, system_prompt_override)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    import asyncio
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Agent failed after {max_retries} attempts: {last_error}"
        ) from last_error

    async def run_streaming(
        self,
        user_prompt: str,
        system_prompt_override: Optional[str] = None,
    ):
        """Run the agent with streaming response.

        Args:
            user_prompt: User prompt to send to the agent
            system_prompt_override: Optional override for system prompt

        Yields:
            Text chunks from the streaming response
        """
        system_prompt = system_prompt_override or self.system_prompt

        async with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        ) as stream:
            async for text in stream.text_stream:
                yield text

            # Track token usage
            message = await stream.get_final_message()
            self.total_tokens_used += message.usage.input_tokens
            self.total_tokens_used += message.usage.output_tokens

    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics.

        Returns:
            Dictionary with token usage information
        """
        return {
            "total_tokens": self.total_tokens_used,
        }

    def reset_token_usage(self) -> None:
        """Reset token usage counter."""
        self.total_tokens_used = 0
