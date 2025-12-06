"""Base OpenAI client with reusable methods."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from openai import OpenAI

from utils.ai.base_client import BaseAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


class BaseOpenAIClient(BaseAIClient):
    """Base client for OpenAI API calls with reusable methods."""

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the OpenAI client.

        Args:
            settings: Voyager seed settings containing OpenAI configuration.
        """
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        print(f"[openai] Initialized OpenAI client with model: {settings.openai_model}")
