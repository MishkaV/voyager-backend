"""LLM-based generator for vibes_country table."""

from pathlib import Path
from typing import Dict, List

from generators.base_generator import BaseGenerator
from utils.database.country_repository import Country, CountryRepository
from utils.database.vibe_country_repository import (
    VibeCountry,
    VibeCountryRepository,
)
from utils.database.vibe_repository import Vibe, VibeRepository
from utils.openai.vibe_country_assignment import (
    VibeCountryAssignment,
    VibeCountryAssignmentClient,
)
from utils.settings.voyager_settings import VoyagerSeedSettings


class VibesCountryGenerator(BaseGenerator):
    """Generator for vibes_country table using LLM."""

    filename = "04_vibes_country.sql"

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the generator.

        Args:
            settings: Voyager seed settings for configuration.
        """
        super().__init__(settings)
        self.country_repo = CountryRepository(settings)
        self.vibe_repo = VibeRepository(settings)
        self.vibe_country_repo = VibeCountryRepository(settings)
        self.openai_client = VibeCountryAssignmentClient(settings)
        print(
            f"[vibes_country] Initialized with batch size: {VibeCountryAssignmentClient.BATCH_SIZE}"
        )

    def generate(self, output_path: Path) -> None:
        """Generate vibes_country records using LLM and write directly to database.

        This method:
        1. Fetches all countries and vibes from the database
        2. Processes countries in batches using OpenAI
        3. Writes results directly to the vibes_country table

        Args:
            output_path: Path parameter (not used, as we write directly to DB).
        """
        print("[vibes_country] Starting generation...")

        # Fetch all countries and vibes
        print("[vibes_country] Fetching countries from database...")
        countries = self.country_repo.get_all()
        print(f"[vibes_country] Found {len(countries)} countries")

        print("[vibes_country] Fetching vibes from database...")
        vibes = self.vibe_repo.get_all()
        print(f"[vibes_country] Found {len(vibes)} vibes")

        if not countries:
            print("[vibes_country] No countries found in database, skipping generation")
            return

        if not vibes:
            raise ValueError("No vibes found in database")

        # Create a mapping of vibe title to vibe ID for quick lookup
        vibe_title_to_id: Dict[str, str] = {vibe.title: vibe.id for vibe in vibes}
        print(f"[vibes_country] Created vibe title mapping ({len(vibe_title_to_id)} vibes)")

        # Create a mapping of country ISO2 to country ID
        country_iso2_to_id: Dict[str, str] = {
            country.iso2: country.id for country in countries
        }

        # Process countries in batches
        batch_size = VibeCountryAssignmentClient.BATCH_SIZE
        total_batches = (len(countries) + batch_size - 1) // batch_size
        print(
            f"[vibes_country] Processing {len(countries)} countries in {total_batches} batch(es) of {batch_size}"
        )

        all_vibe_country_records: List[VibeCountry] = []
        processed_countries = 0

        for batch_idx in range(0, len(countries), batch_size):
            batch_countries = countries[batch_idx : batch_idx + batch_size]
            batch_num = (batch_idx // batch_size) + 1

            print(
                f"[vibes_country] Processing batch {batch_num}/{total_batches} ({len(batch_countries)} countries)..."
            )

            try:
                # Call OpenAI to assign vibes to countries in this batch
                assignments = self.openai_client.assign_vibes_to_countries(
                    vibes, batch_countries
                )

                # Convert assignments to VibeCountry records
                batch_records: List[VibeCountry] = []
                for assignment in assignments:
                    country_id = country_iso2_to_id.get(assignment.country_iso2)
                    if not country_id:
                        print(
                            f"[vibes_country] Warning: Country {assignment.country_iso2} not found in database, skipping"
                        )
                        continue

                    for vibe_title in assignment.vibe_titles:
                        vibe_id = vibe_title_to_id.get(vibe_title)
                        if not vibe_id:
                            print(
                                f"[vibes_country] Warning: Vibe '{vibe_title}' not found in database for country {assignment.country_iso2}, skipping"
                            )
                            continue

                        batch_records.append(
                            VibeCountry(
                                country_id=country_id,
                                vibe_id=vibe_id,
                            )
                        )

                all_vibe_country_records.extend(batch_records)
                processed_countries += len(batch_countries)

                print(
                    f"[vibes_country] Batch {batch_num} completed: {len(batch_records)} vibe-country assignments created"
                )

            except Exception as e:
                print(
                    f"[vibes_country] Error processing batch {batch_num}: {e}"
                )
                raise

        # Insert all records into the database
        if all_vibe_country_records:
            print(
                f"[vibes_country] Inserting {len(all_vibe_country_records)} vibe-country records into database..."
            )
            try:
                # Use insert_many with upsert handling
                # Note: Supabase will handle ON CONFLICT automatically based on the unique constraint
                inserted = self.vibe_country_repo.insert_many(all_vibe_country_records)
                print(
                    f"[vibes_country] Successfully inserted {len(inserted)} vibe-country records"
                )
            except Exception as e:
                # If there are duplicate key conflicts, try inserting one by one
                print(
                    f"[vibes_country] Bulk insert failed (possibly due to duplicates), trying individual inserts: {e}"
                )
                inserted_count = 0
                for record in all_vibe_country_records:
                    try:
                        self.vibe_country_repo.insert(record)
                        inserted_count += 1
                    except Exception as insert_error:
                        # Ignore duplicate key errors
                        if "duplicate" in str(insert_error).lower() or "unique" in str(insert_error).lower():
                            continue
                        raise
                print(
                    f"[vibes_country] Successfully inserted {inserted_count} vibe-country records (some may have been duplicates)"
                )

        print("[vibes_country] Generation completed successfully!")
        print(f"[vibes_country] Statistics:")
        print(f"[vibes_country]   - Countries processed: {processed_countries}")
        print(f"[vibes_country]   - Total vibe-country assignments: {len(all_vibe_country_records)}")

