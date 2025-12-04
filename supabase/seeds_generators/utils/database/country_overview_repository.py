"""Repository and model for country_overview table."""

import dataclasses

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryOverview:
    """Model for country_overview table."""

    id: str
    country_id: str
    body: str
    wikipedia_url: str


class CountryOverviewRepository(BaseRepository[CountryOverview]):
    """Repository for country_overview table."""

    @property
    def _table_name(self) -> str:
        return "country_overview"

    def _model_from_dict(self, data: dict) -> CountryOverview:
        return CountryOverview(
            id=str(data["id"]),
            country_id=str(data["country_id"]),
            body=str(data["body"]),
            wikipedia_url=str(data["wikipedia_url"]),
        )

