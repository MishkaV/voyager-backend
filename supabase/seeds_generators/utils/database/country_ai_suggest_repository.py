"""Repository and model for country_ai_suggests table."""

import dataclasses
from typing import Optional

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryAISuggest:
    """Model for country_ai_suggests table."""

    id: str
    country_id: Optional[str]
    suggest_text: str
    prompt: str


class CountryAISuggestRepository(BaseRepository[CountryAISuggest]):
    """Repository for country_ai_suggests table."""

    @property
    def _table_name(self) -> str:
        return "country_ai_suggests"

    def _model_from_dict(self, data: dict) -> CountryAISuggest:
        return CountryAISuggest(
            id=str(data["id"]),
            country_id=str(data["country_id"]) if data.get("country_id") else None,
            suggest_text=str(data["suggest_text"]),
            prompt=str(data["prompt"]),
        )

