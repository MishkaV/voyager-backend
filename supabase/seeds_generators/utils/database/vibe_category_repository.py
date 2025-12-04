"""Repository and model for vibe_categories table."""

import dataclasses

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class VibeCategory:
    """Model for vibe_categories table."""

    id: str
    title: str


class VibeCategoryRepository(BaseRepository[VibeCategory]):
    """Repository for vibe_categories table."""

    @property
    def _table_name(self) -> str:
        return "vibe_categories"

    def _model_from_dict(self, data: dict) -> VibeCategory:
        return VibeCategory(
            id=str(data["id"]),
            title=str(data["title"]),
        )

