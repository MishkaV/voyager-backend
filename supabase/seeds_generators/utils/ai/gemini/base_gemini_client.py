"""Base Gemini client with reusable methods."""

import mimetypes
import struct
from typing import Any, Dict

from google import genai

from utils.ai.base_client import BaseAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


class BaseGeminiClient(BaseAIClient):
    """Base client for Google Gemini API calls with reusable methods."""

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the Gemini client.

        Args:
            settings: Voyager seed settings containing Gemini configuration.
        """
        super().__init__(settings)
        self.client = genai.Client(api_key=settings.gemini_api_key)
        print(f"[gemini] Initialized Gemini client")

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for this task.

        Returns:
            System prompt string.
        """
        # Not used for audio generation, but required by BaseAIClient
        return ""

    def build_user_prompt(self, **kwargs) -> str:
        """Build the user prompt for this task.

        Args:
            **kwargs: Task-specific parameters.

        Returns:
            User prompt string.
        """
        # Not used for audio generation, but required by BaseAIClient
        return ""

    def parse_response(self, content: str) -> Any:
        """Parse the LLM response and return typed result.

        Args:
            content: Raw content from LLM.

        Returns:
            Parsed result.
        """
        # Not used for audio generation, but required by BaseAIClient
        return content

    def convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Convert PCM audio data to WAV format.

        Generates a WAV file header for the given audio data and parameters.

        Args:
            audio_data: The raw audio data as a bytes object.
            mime_type: Mime type of the audio data (e.g., "audio/L16;rate=24000").

        Returns:
            A bytes object representing the complete WAV file (header + audio data).
        """
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

        # http://soundfile.sapp.org/doc/WaveFormat/
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",          # ChunkID
            chunk_size,       # ChunkSize (total file size - 8 bytes)
            b"WAVE",          # Format
            b"fmt ",          # Subchunk1ID
            16,               # Subchunk1Size (16 for PCM)
            1,                # AudioFormat (1 for PCM)
            num_channels,     # NumChannels
            sample_rate,      # SampleRate
            byte_rate,        # ByteRate
            block_align,      # BlockAlign
            bits_per_sample,  # BitsPerSample
            b"data",          # Subchunk2ID
            data_size         # Subchunk2Size (size of audio data)
        )
        return header + audio_data

    def _parse_audio_mime_type(self, mime_type: str) -> Dict[str, int]:
        """Parse bits per sample and rate from an audio MIME type string.

        Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

        Args:
            mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

        Returns:
            A dictionary with "bits_per_sample" and "rate" keys. Values will be
            integers if found, otherwise defaults to 16 and 24000.
        """
        bits_per_sample = 16
        rate = 24000

        # Extract rate from parameters
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    # Keep rate as default if conversion fails
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    # Keep bits_per_sample as default if conversion fails
                    pass

        return {"bits_per_sample": bits_per_sample, "rate": rate}

