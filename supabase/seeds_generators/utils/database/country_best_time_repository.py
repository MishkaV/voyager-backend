"""Repository and model for country_best_times table."""

import dataclasses

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryBestTime:
    """Model for country_best_times table."""

    id: str
    country_id: str
    title: str
    description: str


class CountryBestTimeRepository(BaseRepository[CountryBestTime]):
    """Repository for country_best_times table."""

    @property
    def _table_name(self) -> str:
        return "country_best_times"

    def _model_from_dict(self, data: dict) -> CountryBestTime:
        return CountryBestTime(
            id=str(data["id"]),
            country_id=str(data["country_id"]),
            title=str(data["title"]),
            description=str(data["description"]),
        )

    def _record_to_dict(self, record: CountryBestTime) -> dict:
        """Convert a CountryBestTime instance to a dictionary for database operations.
        
        Excludes id if it's empty (database will generate it).

        Args:
            record: CountryBestTime instance.

        Returns:
            Dictionary representation of the model.
        """
        from dataclasses import asdict
        
        data = asdict(record)
        # Exclude id if it's empty (database will generate it)
        if not data.get("id"):
            data.pop("id", None)
        return data

