"""Gemini client for generating podcast audio from scripts."""

import mimetypes
from typing import List, Tuple

from google.genai import types

from utils.ai.gemini.base_gemini_client import BaseGeminiClient
from utils.settings.voyager_settings import VoyagerSeedSettings


class PodcastAudioClient(BaseGeminiClient):
    """Client for generating podcast audio using Google Gemini TTS API."""

    # Temperature for generation
    TEMPERATURE: float = 1.0

    # Speaker configurations
    # Format: (speaker_name, voice_name)
    SPEAKER_CONFIGS: List[Tuple[str, str]] = [
        ("Alex", "Puck"),
        ("Maya", "Zephyr"),
    ]

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the podcast audio client.

        Args:
            settings: Voyager seed settings containing Gemini configuration.
        """
        super().__init__(settings)
        print(f"[gemini] Using model: {settings.gemini_tts_model}")

    def generate_podcast_audio(self, script_text: str) -> bytes:
        """Generate podcast audio from script text.

        Args:
            script_text: The podcast script text to convert to audio.

        Returns:
            Complete WAV file as bytes.

        Raises:
            RuntimeError: If audio generation fails or returns empty result.
        """
        try:
            # Prepare content with script text
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=script_text),
                    ],
                ),
            ]

            # Configure speech generation with multi-speaker setup
            speaker_voice_configs = []
            for speaker_name, voice_name in self.SPEAKER_CONFIGS:
                speaker_voice_configs.append(
                    types.SpeakerVoiceConfig(
                        speaker=speaker_name,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        ),
                    )
                )

            generate_content_config = types.GenerateContentConfig(
                temperature=self.TEMPERATURE,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_voice_configs
                    ),
                ),
            )

            # Stream audio chunks and combine them
            audio_chunks = []
            mime_type = None

            for chunk in self.client.models.generate_content_stream(
                model=self.settings.gemini_tts_model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue

                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    if mime_type is None:
                        mime_type = part.inline_data.mime_type
                    audio_chunks.append(part.inline_data.data)
                elif part.text:
                    # Some chunks may contain text, we can log but continue
                    print(f"[gemini] Received text chunk: {part.text[:100]}...")

            if not audio_chunks:
                raise RuntimeError("Gemini API returned no audio data")

            # Combine all audio chunks
            combined_audio = b"".join(audio_chunks)

            # Convert to WAV format if needed
            if mime_type and mime_type.startswith("audio/L"):
                # PCM format, convert to WAV
                wav_audio = self.convert_to_wav(combined_audio, mime_type)
                return wav_audio
            else:
                # Assume it's already in a usable format, or try to guess extension
                file_extension = mimetypes.guess_extension(mime_type) if mime_type else None
                if file_extension is None:
                    # Default to WAV conversion if we can't determine format
                    default_mime = "audio/L16;rate=24000"
                    wav_audio = self.convert_to_wav(combined_audio, default_mime)
                    return wav_audio
                return combined_audio

        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            # Check for quota/rate limit errors
            error_str = str(e).lower()
            if "quota" in error_str or "limit" in error_str or "rate" in error_str:
                raise RuntimeError(f"Gemini API quota/rate limit exceeded: {e}")
            raise RuntimeError(f"Gemini API error during audio generation: {e}")

