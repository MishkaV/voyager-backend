"""Repository and model for countries table."""

import dataclasses
from typing import Optional

from utils.database.base_repository import BaseRepository
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class Country:
    """Model for countries table."""

    id: str
    iso2: str
    name: str
    capital: str
    continent: str
    primary_language: str
    primary_language_code: str
    primary_currency: str
    primary_currency_code: str
    flag_full_patch: str
    background_hex: str


class CountryRepository(BaseRepository[Country]):
    """Repository for countries table."""

    @property
    def _table_name(self) -> str:
        return "countries"

    def _model_from_dict(self, data: dict) -> Country:
        return Country(
            id=str(data["id"]),
            iso2=str(data["iso2"]),
            name=str(data["name"]),
            capital=str(data["capital"]),
            continent=str(data["continent"]),
            primary_language=str(data["primary_language"]),
            primary_language_code=str(data["primary_language_code"]),
            primary_currency=str(data["primary_currency"]),
            primary_currency_code=str(data["primary_currency_code"]),
            flag_full_patch=str(data["flag_full_patch"]),
            background_hex=str(data["background_hex"]),
        )

    def get_by_iso2(self, iso2: str) -> Optional[Country]:
        """Get a country by its ISO2 code.

        Args:
            iso2: ISO2 code (e.g., "US").

        Returns:
            Country instance if found, None otherwise.
        """
        response = (
            self.client.table(self._table_name)
            .select("*")
            .eq("iso2", iso2.upper())
            .execute()
        )
        if response.data:
            return self._model_from_dict(response.data[0])
        return None

