"""LLM-based generator for podcast audio files."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Tuple

from generators.base_generator import BaseGenerator
from utils.database.country_repository import Country, CountryRepository
from utils.ai.gemini.podcast_audio_client import PodcastAudioClient
from utils.settings.voyager_settings import VoyagerSeedSettings
from utils.storage.supabase_storage import SupabaseStorageClient


class PodcastAudioGenerator(BaseGenerator):
    """Generator for podcast audio files using Gemini TTS and uploading to Supabase Storage."""

    # Number of parallel workers for processing countries
    MAX_WORKERS: int = 5

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the generator.

        Args:
            settings: Voyager seed settings for configuration.
        """
        super().__init__(settings)
        self.country_repo = CountryRepository(settings)
        self.gemini_client = PodcastAudioClient(settings)
        self.storage_client = SupabaseStorageClient(settings)
        self.scripts_bucket_name = "podcasts_scripts"
        self.audio_bucket_name = "podcasts"
        self._stats_lock = Lock()
        self._quota_exceeded = False
        self._quota_lock = Lock()
        
        # Create temp directory in seeds_generators for manual uploads
        seeds_generators_dir = Path(__file__).resolve().parent.parent.parent
        self.temp_audio_dir = seeds_generators_dir / "temp_podcasts_audio"
        self.temp_audio_dir.mkdir(parents=True, exist_ok=True)
        
        print(
            f"[podcast_audio] Initialized with storage buckets: {self.scripts_bucket_name} (scripts), {self.audio_bucket_name} (audio)"
        )
        print(
            f"[podcast_audio] Parallel workers: {self.MAX_WORKERS}"
        )
        print(
            f"[podcast_audio] Temp audio directory: {self.temp_audio_dir}"
        )

    def _check_quota_exceeded(self) -> bool:
        """Check if quota has been exceeded.

        Returns:
            True if quota exceeded, False otherwise.
        """
        with self._quota_lock:
            return self._quota_exceeded

    def _set_quota_exceeded(self) -> None:
        """Mark that quota has been exceeded."""
        with self._quota_lock:
            self._quota_exceeded = True

    def _process_country(
        self, country: Country, temp_path: Path
    ) -> Tuple[str, str, bool, bool]:
        """Process a single country: download script, generate audio, and upload to storage.

        Args:
            country: Country to process.
            temp_path: Path to temporary directory for audio files.

        Returns:
            Tuple of (country_iso2, country_name, success, skipped).
        """
        try:
            # Check if audio already exists in storage
            audio_storage_path = f"{country.iso2}.wav"
            if self.storage_client.file_exists(self.audio_bucket_name, audio_storage_path):
                print(
                    f"[podcast_audio] ⊘ Audio for {country.name} ({country.iso2}) already exists, skipping"
                )
                return (country.iso2, country.name, False, True)

            # Check if script exists
            script_storage_path = f"{country.iso2}.txt"
            if not self.storage_client.file_exists(self.scripts_bucket_name, script_storage_path):
                print(
                    f"[podcast_audio] ⊘ Script for {country.name} ({country.iso2}) not found, skipping"
                )
                return (country.iso2, country.name, False, True)

            # Check quota before proceeding
            if self._check_quota_exceeded():
                print(
                    f"[podcast_audio] ⊘ Quota exceeded, skipping {country.name} ({country.iso2})"
                )
                return (country.iso2, country.name, False, True)

            print(
                f"[podcast_audio] Generating audio for {country.name} ({country.iso2})..."
            )

            # Download script from storage
            script_content = self.storage_client.download_file(
                bucket=self.scripts_bucket_name,
                storage_path=script_storage_path,
            )
            script_text = script_content.decode("utf-8")

            # Generate audio using Gemini
            # Note: Create a new client per thread to be safe
            gemini_client = PodcastAudioClient(self.settings)
            audio_data = gemini_client.generate_podcast_audio(script_text)

            # Save audio to temp directory (for manual uploads if needed)
            temp_file_path = temp_path / f"{country.iso2}.wav"
            with temp_file_path.open("wb") as f:
                f.write(audio_data)

            # Upload to Supabase Storage
            self.storage_client.upload_file(
                file_path=temp_file_path,
                bucket=self.audio_bucket_name,
                storage_path=audio_storage_path,
            )

            print(
                f"[podcast_audio] ✓ Uploaded audio for {country.name} ({country.iso2})"
            )
            return (country.iso2, country.name, True, False)

        except RuntimeError as e:
            error_str = str(e).lower()
            if "quota" in error_str or "limit" in error_str:
                # Mark quota as exceeded
                self._set_quota_exceeded()
                print(
                    f"[podcast_audio] ✗ Quota exceeded while processing {country.name} ({country.iso2}): {e}"
                )
                return (country.iso2, country.name, False, False)
            else:
                print(
                    f"[podcast_audio] ✗ Error processing {country.name} ({country.iso2}): {e}"
                )
                return (country.iso2, country.name, False, False)
        except Exception as e:
            print(
                f"[podcast_audio] ✗ Error processing {country.name} ({country.iso2}): {e}"
            )
            return (country.iso2, country.name, False, False)

    def generate(self, output_path: Path) -> None:
        """Generate podcast audio files using Gemini TTS and upload to Supabase Storage.

        This method:
        1. Fetches all countries from the database
        2. Processes countries in parallel using ThreadPoolExecutor
        3. Downloads scripts from "podcasts_scripts" bucket
        4. Generates audio using Gemini TTS
        5. Uploads audio to "podcasts" bucket

        Args:
            output_path: Path parameter (not used, as we upload directly to Storage).
        """
        print("[podcast_audio] Starting generation...")

        # Fetch all countries
        print("[podcast_audio] Fetching countries from database...")
        countries = self.country_repo.get_all()
        print(f"[podcast_audio] Found {len(countries)} countries")

        if not countries:
            print("[podcast_audio] No countries found in database, skipping generation")
            return

        print(
            f"[podcast_audio] Processing {len(countries)} countries in parallel (max {self.MAX_WORKERS} workers)..."
        )

        processed_countries = 0
        uploaded_count = 0
        skipped_count = 0
        failed_count = 0

        # Use temp directory in seeds_generators (files will persist for manual uploads)
        temp_path = self.temp_audio_dir

        # Process countries in parallel
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                # Submit all tasks
                future_to_country = {
                    executor.submit(self._process_country, country, temp_path): country
                    for country in countries
                }

                # Process completed tasks
                for future in as_completed(future_to_country):
                    # Check if quota exceeded and stop submitting new tasks
                    if self._check_quota_exceeded():
                        # Cancel remaining futures that haven't started
                        for f in future_to_country:
                            if not f.done():
                                f.cancel()
                        break

                    country = future_to_country[future]
                    try:
                        country_iso2, country_name, success, skipped = future.result()
                        processed_countries += 1

                        with self._stats_lock:
                            if skipped:
                                skipped_count += 1
                            elif success:
                                uploaded_count += 1
                            else:
                                failed_count += 1

                    except Exception as e:
                        failed_count += 1
                        print(
                            f"[podcast_audio] ✗ Unexpected error processing {country.name} ({country.iso2}): {e}"
                        )

        print("[podcast_audio] Generation completed!")
        print(f"[podcast_audio] Audio files saved to: {self.temp_audio_dir}")
        print(f"[podcast_audio] Statistics:")
        print(f"[podcast_audio]   - Countries processed: {processed_countries}")
        print(f"[podcast_audio]   - Audio files uploaded: {uploaded_count}")
        if skipped_count > 0:
            print(f"[podcast_audio]   - Skipped (already exist or script missing): {skipped_count}")
        if failed_count > 0:
            print(f"[podcast_audio]   - Failed: {failed_count}")
        if self._check_quota_exceeded():
            print(f"[podcast_audio]   - ⚠ Quota/rate limit exceeded - some countries may not have been processed")

