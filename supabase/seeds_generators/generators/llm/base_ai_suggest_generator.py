"""Base generator for AI suggestions with common database insertion logic."""

from pathlib import Path
from typing import List

from generators.base_generator import BaseGenerator
from utils.database.country_ai_suggest_repository import (
    CountryAISuggest,
    CountryAISuggestRepository,
)
from utils.settings.voyager_settings import VoyagerSeedSettings


class BaseAISuggestGenerator(BaseGenerator):
    """Base generator for AI suggestions with common database insertion logic."""

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the generator.

        Args:
            settings: Voyager seed settings for configuration.
        """
        super().__init__(settings)
        self.country_ai_suggest_repo = CountryAISuggestRepository(settings)

    def _insert_records(self, records: List[CountryAISuggest], log_prefix: str) -> None:
        """Insert records into the database with error handling.

        Args:
            records: List of CountryAISuggest records to insert.
            log_prefix: Prefix for log messages (e.g., "[general_ai_suggests]").
        """
        if not records:
            return

        print(
            f"{log_prefix} Inserting {len(records)} suggestion records into database..."
        )
        try:
            # Use insert_many with upsert handling
            inserted = self.country_ai_suggest_repo.insert_many(records)
            print(
                f"{log_prefix} Successfully inserted {len(inserted)} suggestion records"
            )
        except Exception as e:
            # If there are duplicate key conflicts, try inserting one by one
            print(
                f"{log_prefix} Bulk insert failed (possibly due to duplicates), trying individual inserts: {e}"
            )
            inserted_count = 0
            for record in records:
                try:
                    self.country_ai_suggest_repo.insert(record)
                    inserted_count += 1
                except Exception as insert_error:
                    # Ignore duplicate key errors
                    if "duplicate" in str(insert_error).lower() or "unique" in str(insert_error).lower():
                        continue
                    raise
            print(
                f"{log_prefix} Successfully inserted {inserted_count} suggestion records (some may have been duplicates)"
            )

