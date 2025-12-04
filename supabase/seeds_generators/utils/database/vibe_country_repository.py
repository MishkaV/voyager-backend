"""Repository and model for vibes_country table."""

import dataclasses
from typing import List

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class VibeCountry:
    """Model for vibes_country table."""

    country_id: str
    vibe_id: str


class VibeCountryRepository(BaseRepository[VibeCountry]):
    """Repository for vibes_country table."""

    @property
    def _table_name(self) -> str:
        return "vibes_country"

    def _model_from_dict(self, data: dict) -> VibeCountry:
        return VibeCountry(
            country_id=str(data["country_id"]),
            vibe_id=str(data["vibe_id"]),
        )

    def insert_many(self, records: List[VibeCountry]) -> List[VibeCountry]:
        """Insert multiple records into the table.

        Override to handle composite primary key (no 'id' field).

        Args:
            records: List of model instances to insert.

        Returns:
            List of inserted model instances.
        """
        if not records:
            return []
        data = [self._record_to_dict(record) for record in records]
        response = self.client.table(self._table_name).insert(data).execute()
        return [self._model_from_dict(row) for row in response.data]

