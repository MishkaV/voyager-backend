"""Base OpenAI client with reusable methods."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from openai import OpenAI

from utils.settings.voyager_settings import VoyagerSeedSettings


class BaseOpenAIClient(ABC):
    """Base client for OpenAI API calls with reusable methods."""

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the OpenAI client.

        Args:
            settings: Voyager seed settings containing OpenAI configuration.
        """
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        print(f"[openai] Initialized OpenAI client with model: {settings.openai_model}")

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this task.

        Returns:
            System prompt string.
        """
        pass

    @abstractmethod
    def build_user_prompt(self, **kwargs) -> str:
        """Build the user prompt for this task.

        Args:
            **kwargs: Task-specific parameters.

        Returns:
            User prompt string.
        """
        pass

    @abstractmethod
    def parse_response(self, content: str) -> Any:
        """Parse the LLM response and return typed result.

        Args:
            content: Raw JSON content from LLM.

        Returns:
            Parsed result (type depends on task).

        Raises:
            RuntimeError: If response cannot be parsed.
        """
        pass

    def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Dict[str, str] | None = None,
    ) -> str:
        """Make a call to OpenAI API.

        Args:
            system_prompt: System prompt for the API call.
            user_prompt: User prompt for the API call.
            response_format: Optional response format specification.

        Returns:
            Content string from the API response.

        Raises:
            RuntimeError: If API call fails or returns empty response.
        """
        try:
            params = {
                "model": self.settings.openai_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
            if response_format:
                params["response_format"] = response_format

            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("LLM returned empty response")

            return content

        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"OpenAI API error: {e}")

    def _parse_json(self, content: str) -> Dict[str, Any] | List[Any]:
        """Parse JSON content from LLM response.

        Args:
            content: JSON string to parse.

        Returns:
            Parsed JSON object (dict or list).

        Raises:
            RuntimeError: If JSON is invalid.
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"LLM returned invalid JSON: {e}\nRaw output: {content[:500]}"
            )

    def execute(self, **kwargs) -> Any:
        """Execute the task with given parameters.

        Args:
            **kwargs: Task-specific parameters.

        Returns:
            Parsed result from the task.

        Raises:
            RuntimeError: If task execution fails.
        """
        system_prompt = self.system_prompt
        user_prompt = self.build_user_prompt(**kwargs)

        content = self._call_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
        )

        return self.parse_response(content)

