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

