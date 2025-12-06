"""LLM-based generator for podcast scripts."""

import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import List, Tuple

from generators.base_generator import BaseGenerator
from utils.database.country_repository import Country, CountryRepository
from utils.ai.openai.podcast_script_assignment import (
    PodcastScriptAssignment,
    PodcastScriptAssignmentClient,
)
from utils.settings.voyager_settings import VoyagerSeedSettings
from utils.storage.supabase_storage import SupabaseStorageClient
from utils.wiki.wikipedia_url import generate_wikipedia_url


class PodcastScriptGenerator(BaseGenerator):
    """Generator for podcast scripts using LLM and uploading to Supabase Storage."""

    # Number of parallel workers for processing countries
    MAX_WORKERS: int = 5

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the generator.

        Args:
            settings: Voyager seed settings for configuration.
        """
        super().__init__(settings)
        self.country_repo = CountryRepository(settings)
        self.openai_client = PodcastScriptAssignmentClient(settings)
        self.storage_client = SupabaseStorageClient(settings)
        self.bucket_name = "podcasts_scripts"
        self._stats_lock = Lock()
        print(
            f"[podcast_scripts] Initialized with batch size: {PodcastScriptAssignmentClient.BATCH_SIZE}"
        )
        print(
            f"[podcast_scripts] Storage bucket: {self.bucket_name}"
        )
        print(
            f"[podcast_scripts] Parallel workers: {self.MAX_WORKERS}"
        )

    def _process_country(
        self, country: Country, temp_path: Path
    ) -> Tuple[str, str, bool, bool]:
        """Process a single country: generate script and upload to storage.

        Args:
            country: Country to process.
            temp_path: Path to temporary directory for script files.

        Returns:
            Tuple of (country_iso2, country_name, success, skipped).
        """
        try:
            # Check if script already exists in storage
            storage_path = f"{country.iso2}.txt"
            if self.storage_client.file_exists(self.bucket_name, storage_path):
                print(
                    f"[podcast_scripts] ⊘ Script for {country.name} ({country.iso2}) already exists, skipping"
                )
                return (country.iso2, country.name, False, True)

            # Generate Wikipedia URL
            wikipedia_url = generate_wikipedia_url(country.name)
            print(
                f"[podcast_scripts] Generating script for {country.name} ({country.iso2})..."
            )

            # Call OpenAI to get script for this country
            # Note: OpenAI client should be thread-safe, but we create a new one per thread to be safe
            openai_client = PodcastScriptAssignmentClient(self.settings)
            assignment: PodcastScriptAssignment = openai_client.get_script_for_country(
                country=country, wikipedia_url=wikipedia_url
            )

            # Save script to temporary file
            temp_file_path = temp_path / f"{country.iso2}.txt"
            with temp_file_path.open("w", encoding="utf-8") as f:
                f.write(assignment.script)

            # Upload to Supabase Storage
            self.storage_client.upload_file(
                file_path=temp_file_path,
                bucket=self.bucket_name,
                storage_path=storage_path,
            )

            print(
                f"[podcast_scripts] ✓ Uploaded script for {country.name} ({country.iso2})"
            )
            return (country.iso2, country.name, True, False)

        except Exception as e:
            print(
                f"[podcast_scripts] ✗ Error processing {country.name} ({country.iso2}): {e}"
            )
            return (country.iso2, country.name, False, False)

    def generate(self, output_path: Path) -> None:
        """Generate podcast scripts using LLM and upload to Supabase Storage.

        This method:
        1. Fetches all countries from the database
        2. Processes countries in parallel using ThreadPoolExecutor
        3. Uploads scripts to Supabase Storage bucket "podcasts_scripts"

        Args:
            output_path: Path parameter (not used, as we upload directly to Storage).
        """
        print("[podcast_scripts] Starting generation...")

        # Fetch all countries
        print("[podcast_scripts] Fetching countries from database...")
        countries = self.country_repo.get_all()
        print(f"[podcast_scripts] Found {len(countries)} countries")

        if not countries:
            print("[podcast_scripts] No countries found in database, skipping generation")
            return

        print(
            f"[podcast_scripts] Processing {len(countries)} countries in parallel (max {self.MAX_WORKERS} workers)..."
        )

        processed_countries = 0
        uploaded_count = 0
        skipped_count = 0
        failed_count = 0

        # Create temporary directory for script files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Process countries in parallel
            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                # Submit all tasks
                future_to_country = {
                    executor.submit(self._process_country, country, temp_path): country
                    for country in countries
                }

                # Process completed tasks
                for future in as_completed(future_to_country):
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
                            f"[podcast_scripts] ✗ Unexpected error processing {country.name} ({country.iso2}): {e}"
                        )

        print("[podcast_scripts] Generation completed!")
        print(f"[podcast_scripts] Statistics:")
        print(f"[podcast_scripts]   - Countries processed: {processed_countries}")
        print(f"[podcast_scripts]   - Scripts uploaded: {uploaded_count}")
        if skipped_count > 0:
            print(f"[podcast_scripts]   - Scripts skipped (already exist): {skipped_count}")
        if failed_count > 0:
            print(f"[podcast_scripts]   - Failed: {failed_count}")

