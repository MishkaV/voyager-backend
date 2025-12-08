"""LLM-based generator for country_podcasts table."""

import io
import re
import wave
from pathlib import Path
from typing import List, Optional

from generators.base_generator import BaseGenerator
from utils.database.country_podcast_repository import (
    CountryPodcast,
    CountryPodcastRepository,
)
from utils.database.country_repository import Country, CountryRepository
from utils.database.vibe_country_repository import VibeCountryRepository
from utils.database.vibe_repository import VibeRepository
from utils.settings.voyager_settings import VoyagerSeedSettings
from utils.storage.supabase_storage import SupabaseStorageClient


class CountryPodcastGenerator(BaseGenerator):
    """Generator for country_podcasts table by processing audio files in storage."""

    # Predefined subtitle phrases
    SUBTITLES = [
        "What to know before you go",
        "Essential travel insights",
        "Your guide to exploring",
        "Discover what makes it special",
        "Insights for your journey",
    ]

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the generator.

        Args:
            settings: Voyager seed settings for configuration.
        """
        super().__init__(settings)
        self.country_repo = CountryRepository(settings)
        self.podcast_repo = CountryPodcastRepository(settings)
        self.vibe_country_repo = VibeCountryRepository(settings)
        self.vibe_repo = VibeRepository(settings)
        self.storage_client = SupabaseStorageClient(settings)
        self.audio_bucket_name = "podcasts"
        self.scripts_bucket_name = "podcasts_scripts"
        print(
            f"[country_podcast] Initialized with storage bucket: {self.audio_bucket_name}"
        )

    def _get_audio_duration(self, audio_data: bytes) -> int:
        """Calculate audio duration in seconds from WAV file data.

        Args:
            audio_data: WAV file content as bytes.

        Returns:
            Duration in seconds (rounded to nearest integer).

        Raises:
            ValueError: If audio data cannot be parsed.
        """
        try:
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            with wave.open(audio_file, "rb") as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration_sec = frames / float(sample_rate)
                return int(round(duration_sec))
        except Exception as e:
            raise ValueError(f"Failed to parse WAV file: {e}")

    def _get_country_vibes(self, country_id: str) -> List[str]:
        """Get vibe titles for a country.

        Args:
            country_id: UUID of the country.

        Returns:
            List of vibe titles (2-3 vibes).
        """
        try:
            # Get vibe_ids for this country
            vibe_country_response = (
                self.vibe_country_repo.client.table(self.vibe_country_repo._table_name)
                .select("vibe_id")
                .eq("country_id", country_id)
                .execute()
            )
            
            if not vibe_country_response.data:
                return []
            
            vibe_ids = [vc["vibe_id"] for vc in vibe_country_response.data]
            
            # Get vibe titles
            if not vibe_ids:
                return []
            
            # Query vibes table for these IDs
            vibes_response = (
                self.vibe_repo.client.table(self.vibe_repo._table_name)
                .select("title")
                .in_("id", vibe_ids)
                .execute()
            )
            
            if not vibes_response.data:
                return []
            
            vibe_titles = [v["title"] for v in vibes_response.data]
            
            # Return 2-3 vibes
            return vibe_titles[:3]
            
        except Exception as e:
            print(f"[country_podcast] Warning: Failed to get vibes for country: {e}")
            return []

    def _generate_title(self, country_name: str, country_id: str) -> str:
        """Generate podcast title in format: "{Country}: {Vibe1}, {Vibe2}, {Vibe3}".

        Args:
            country_name: Name of the country.
            country_id: UUID of the country.

        Returns:
            Formatted title string.
        """
        vibes = self._get_country_vibes(country_id)
        
        if vibes:
            # Join 2-3 vibes with commas
            vibes_str = ", ".join(vibes)
            return f"{country_name}: {vibes_str}"
        else:
            # Fallback if no vibes found
            return f"{country_name}: Travel insights"

    def _get_subtitle(self, index: int) -> str:
        """Get a subtitle from the predefined list, rotating based on index.

        Args:
            index: Index to determine which subtitle to use.

        Returns:
            Subtitle string.
        """
        return self.SUBTITLES[index % len(self.SUBTITLES)]

    def _process_audio_file(
        self, filename: str
    ) -> Optional[CountryPodcast]:
        """Process a single audio file and create a podcast record.

        Args:
            filename: Name of the audio file (e.g., "US.wav").

        Returns:
            CountryPodcast record if successful, None if skipped.
        """
        # Extract ISO2 code from filename (format: {iso2}.wav)
        match = re.match(r"^([A-Z]{2})\.wav$", filename, re.IGNORECASE)
        if not match:
            print(
                f"[country_podcast] ⊘ Skipping file with unexpected format: {filename}"
            )
            return None

        iso2 = match.group(1).upper()

        # Get country by ISO2
        country = self.country_repo.get_by_iso2(iso2)
        if not country:
            print(
                f"[country_podcast] ⊘ Country not found for ISO2 {iso2}, skipping {filename}"
            )
            return None

        # Check if podcast already exists for this country
        try:
            existing = self.podcast_repo.client.table(
                self.podcast_repo._table_name
            ).select("id").eq("country_id", country.id).limit(1).execute()
            if existing.data:
                print(
                    f"[country_podcast] ⊘ Podcast already exists for {country.name} ({iso2}), skipping"
                )
                return None
        except Exception as e:
            # If check fails, continue processing (might be a new record)
            print(
                f"[country_podcast] Warning: Could not check for existing podcast: {e}"
            )

        try:
            # Download audio file to get duration
            print(
                f"[country_podcast] Processing {country.name} ({iso2})..."
            )
            audio_data = self.storage_client.download_file(
                bucket=self.audio_bucket_name,
                storage_path=filename,
            )

            # Calculate duration
            duration_sec = self._get_audio_duration(audio_data)

            # Generate title and subtitle using vibes
            title = self._generate_title(country.name, country.id)
            # Use country index for subtitle rotation
            subtitle_index = hash(country.iso2) % len(self.SUBTITLES)
            subtitle = self._get_subtitle(subtitle_index)

            # Create podcast record
            audio_full_patch = f"{self.audio_bucket_name}/{filename}"
            podcast = CountryPodcast(
                id="",  # Will be generated by database
                country_id=country.id,
                audio_full_patch=audio_full_patch,
                title=title,
                subtitle=subtitle,
                duration_sec=duration_sec,
            )

            print(
                f"[country_podcast] ✓ Created record for {country.name} ({iso2}): {title}"
            )
            return podcast

        except Exception as e:
            print(
                f"[country_podcast] ✗ Error processing {country.name} ({iso2}): {e}"
            )
            return None

    def generate(self, output_path: Path) -> None:
        """Generate country_podcasts records by processing audio files in storage.

        This method:
        1. Lists all audio files in the "podcasts" storage bucket
        2. For each file, extracts country info and audio metadata
        3. Generates title and subtitle
        4. Inserts records into the country_podcasts table

        Args:
            output_path: Path parameter (not used, as we write directly to DB).
        """
        print("[country_podcast] Starting generation...")

        # List all files in the podcasts bucket
        print(f"[country_podcast] Listing files in bucket '{self.audio_bucket_name}'...")
        try:
            files = self.storage_client.client.storage.from_(self.audio_bucket_name).list()
        except Exception as e:
            print(f"[country_podcast] ✗ Failed to list files in bucket: {e}")
            return

        if not files:
            print(f"[country_podcast] No files found in bucket '{self.audio_bucket_name}'")
            return

        # Filter for .wav files only
        # Handle both dict and object responses from Supabase storage
        wav_files = []
        for file_info in files:
            # Handle dict response
            if isinstance(file_info, dict):
                filename = file_info.get("name", "")
            # Handle object response (has name attribute)
            elif hasattr(file_info, "name"):
                filename = file_info.name
            else:
                # Try to convert to string and extract filename
                filename = str(file_info)
            
            if filename and filename.endswith(".wav"):
                wav_files.append(filename)

        print(f"[country_podcast] Found {len(wav_files)} WAV files")

        if not wav_files:
            print("[country_podcast] No WAV files found, skipping generation")
            return

        # Process each audio file
        podcast_records: List[CountryPodcast] = []
        processed_count = 0
        skipped_count = 0
        failed_count = 0

        for filename in wav_files:
            podcast = self._process_audio_file(filename)
            if podcast:
                podcast_records.append(podcast)
                processed_count += 1
            else:
                skipped_count += 1

        # Insert records into the database
        if podcast_records:
            print(
                f"[country_podcast] Inserting {len(podcast_records)} podcast records into database..."
            )
            try:
                # Use insert_many with upsert handling
                inserted = self.podcast_repo.insert_many(podcast_records)
                print(
                    f"[country_podcast] Successfully inserted {len(inserted)} podcast records"
                )
            except Exception as e:
                # If there are duplicate key conflicts, try inserting one by one
                print(
                    f"[country_podcast] Bulk insert failed (possibly due to duplicates), trying individual inserts: {e}"
                )
                inserted_count = 0
                for record in podcast_records:
                    try:
                        self.podcast_repo.insert(record)
                        inserted_count += 1
                    except Exception as insert_error:
                        # Ignore duplicate key errors
                        error_str = str(insert_error).lower()
                        if "duplicate" in error_str or "unique" in error_str:
                            skipped_count += 1
                            continue
                        raise
                print(
                    f"[country_podcast] Successfully inserted {inserted_count} podcast records (some may have been duplicates)"
                )

        print("[country_podcast] Generation completed!")
        print(f"[country_podcast] Statistics:")
        print(f"[country_podcast]   - Files processed: {processed_count}")
        print(f"[country_podcast]   - Records inserted: {len(podcast_records)}")
        if skipped_count > 0:
            print(f"[country_podcast]   - Skipped: {skipped_count}")
        if failed_count > 0:
            print(f"[country_podcast]   - Failed: {failed_count}")

