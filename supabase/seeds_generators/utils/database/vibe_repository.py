"""Repository and model for vibes table."""

import dataclasses

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class Vibe:
    """Model for vibes table."""

    id: str
    category_id: str
    title: str
    icon_emoji: str


class VibeRepository(BaseRepository[Vibe]):
    """Repository for vibes table."""

    @property
    def _table_name(self) -> str:
        return "vibes"

    def _model_from_dict(self, data: dict) -> Vibe:
        return Vibe(
            id=str(data["id"]),
            category_id=str(data["category_id"]),
            title=str(data["title"]),
            icon_emoji=str(data["icon_emoji"]),
        )

