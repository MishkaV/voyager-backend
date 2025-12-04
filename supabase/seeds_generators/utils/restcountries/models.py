"""Data models for RestCountries API responses."""

import dataclasses
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from typing import Any


@dataclasses.dataclass
class Flags:
    """Flags data from RestCountries API."""

    png: str
    svg: str


@dataclasses.dataclass
class Name:
    """Name data from RestCountries API."""

    common: str
    official: str


@dataclasses.dataclass
class Currency:
    """Currency data from RestCountries API."""

    name: str
    symbol: str = ""


@dataclasses.dataclass
class RestCountryResponse:
    """Country data model matching RestCountries API response structure."""

    cca2: str
    name: Name
    capital: List[str]
    continents: List[str]
    languages: Dict[str, str]
    currencies: Dict[str, Currency]
    flags: Flags

    def to_country_data(self, country_data_class: type) -> "Any":
        """Convert RestCountryResponse to CountryData for database insertion.

        Args:
            country_data_class: The CountryData class to instantiate.

        Returns:
            CountryData object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        iso2 = self.cca2.upper()

        capital = self.capital[0] if self.capital else "None"
        continent = self.continents[0]

        lang_code, lang_name = next(iter(self.languages.items()))
        primary_language = lang_name
        primary_language_code = lang_code.upper()

        curr_code, curr_obj = next(iter(self.currencies.items()))
        primary_currency_code = curr_code.upper()

        primary_currency = curr_obj.name or primary_currency_code

        return country_data_class(
            iso2=iso2,
            name=self.name.common,
            capital=capital,
            continent=continent,
            primary_language=primary_language,
            primary_language_code=primary_language_code,
            primary_currency=primary_currency,
            primary_currency_code=primary_currency_code,
            flag_full_path="",  # Will be set after upload
            background_hex="#CC000000",  # Will be set after palette extraction
        )

