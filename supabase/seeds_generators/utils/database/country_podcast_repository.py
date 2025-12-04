"""Repository and model for country_podcasts table."""

import dataclasses

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryPodcast:
    """Model for country_podcasts table."""

    id: str
    country_id: str
    audio_full_patch: str
    title: str
    subtitle: str
    duration_sec: int


class CountryPodcastRepository(BaseRepository[CountryPodcast]):
    """Repository for country_podcasts table."""

    @property
    def _table_name(self) -> str:
        return "country_podcasts"

    def _model_from_dict(self, data: dict) -> CountryPodcast:
        return CountryPodcast(
            id=str(data["id"]),
            country_id=str(data["country_id"]),
            audio_full_patch=str(data["audio_full_patch"]),
            title=str(data["title"]),
            subtitle=str(data["subtitle"]),
            duration_sec=int(data["duration_sec"]),
        )

