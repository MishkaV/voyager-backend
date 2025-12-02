"""Generate countries seed SQL file from RestCountries API."""

import dataclasses
from pathlib import Path
from typing import Dict, List

import requests

from base_generator import BaseGenerator
from utils.settings.voyager_settings import VoyagerSeedSettings
from utils.storage.supabase_storage import SupabaseStorageClient


def _filter_dataclass_fields(data: dict, dataclass_type: type) -> dict:
    """Filter dictionary to only include fields that exist in the dataclass.
    
    Args:
        data: Dictionary with data (may contain extra fields).
        dataclass_type: Dataclass type to filter against.
        
    Returns:
        Filtered dictionary with only known fields.
    """
    if not dataclasses.is_dataclass(dataclass_type):
        return data
    
    field_names = {field.name for field in dataclasses.fields(dataclass_type)}
    return {key: value for key, value in data.items() if key in field_names}


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

    def to_country_data(self) -> "CountryData":
        """Convert RestCountryResponse to CountryData for database insertion.

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

        flag_url = self.flags.png or self.flags.svg

        return CountryData(
            iso2=iso2,
            name=self.name.common,
            capital=capital,
            continent=continent,
            primary_language=primary_language,
            primary_language_code=primary_language_code,
            primary_currency=primary_currency,
            primary_currency_code=primary_currency_code,
            flag_url=flag_url,
        )


@dataclasses.dataclass
class CountryData:
    """Processed country data for database insertion."""

    iso2: str
    name: str
    capital: str
    continent: str
    primary_language: str
    primary_language_code: str
    primary_currency: str
    primary_currency_code: str
    flag_url: str


class CountriesGenerator(BaseGenerator):
    """Generator for countries seed SQL file."""

    filename = "03_countries.sql"
    RESTCOUNTRIES_FIELDS = "cca2,name,capital,continents,languages,currencies,flags"
    
    # ISO2 codes of countries to ignore (e.g., territories, uninhabited regions)
    IGNORED_COUNTRIES: List[str] = [
        "AQ",  # Antarctica
    ]
    IGNORED_CONTINENTS: List[str] = [
        "Antarctica",
    ]

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the countries generator."""
        super().__init__(settings)
        self.storage_client: SupabaseStorageClient = SupabaseStorageClient(self.settings)
        print(
            f"[countries] Storage client initialized, will upload flags to {self.settings.supabase_bucket_name_flags}"
        )

    def _fetch_countries(self) -> List[RestCountryResponse]:
        """Fetch country data from RestCountries API.

        Returns:
            List of RestCountryResponse objects.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"{self.settings.restcountries_base_url}/all"
        params = {"fields": self.RESTCOUNTRIES_FIELDS}

        print(f"[countries] Fetching countries from {url}...")

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"[countries] Fetched {len(data)} countries from API")

        countries: List[RestCountryResponse] = []
        ignored_count = 0
        for country_dict in data:
            # Skip ignored countries by ISO2 code
            cca2 = country_dict.get("cca2", "").upper()
            if cca2 in self.IGNORED_COUNTRIES:
                ignored_count += 1
                print(f"[countries] Ignoring country: {cca2} ({country_dict.get('name', {}).get('common', 'Unknown')})")
                continue
            
            # Skip countries in ignored continents
            continents = country_dict.get("continents", [])
            if any(continent in self.IGNORED_CONTINENTS for continent in continents):
                ignored_count += 1
                country_name = country_dict.get('name', {}).get('common', 'Unknown')
                print(f"[countries] Ignoring country in ignored continent: {cca2} ({country_name})")
                continue
            
            # Convert nested dicts to dataclasses, filtering unknown fields
            country_dict["name"] = Name(**_filter_dataclass_fields(country_dict["name"], Name))
            country_dict["flags"] = Flags(**_filter_dataclass_fields(country_dict["flags"], Flags))
            # Convert currencies dict
            currencies = {}
            for code, curr_data in country_dict["currencies"].items():
                currencies[code] = Currency(**_filter_dataclass_fields(curr_data, Currency))
            country_dict["currencies"] = currencies

            country = RestCountryResponse(**_filter_dataclass_fields(country_dict, RestCountryResponse))
            countries.append(country)

        print(f"[countries] Parsed {len(countries)} countries (ignored {ignored_count})")
        return countries

    def _upload_flag_to_storage(self, flag_url: str, iso2: str, bucket: str) -> str:
        """Upload country flag to Supabase Storage.

        Args:
            flag_url: Original flag URL from RestCountries API.
            iso2: Country ISO2 code (e.g., "US").
            bucket: Storage bucket name.

        Returns:
            Public URL of the uploaded flag.

        Raises:
            ValueError: If flag URL is empty or upload fails.
        """
        if not flag_url:
            raise ValueError(f"Flag URL cannot be empty for country {iso2}")

        storage_path = f"{iso2}.png"
        return self.storage_client.upload_from_url(flag_url, bucket, storage_path)

    def generate(self, output_path: Path) -> None:
        """Generate countries seed SQL file.

        Args:
            output_path: Path where the SQL file should be written.

        Raises:
            ValueError: If required country data is missing.
            Exception: If flag upload fails.
        """
        rest_countries = self._fetch_countries()

        rows: List[str] = []
        uploaded_count = 0
        fallback_count = 0

        print(f"[countries] Processing {len(rest_countries)} countries...")

        bucket = self.settings.supabase_bucket_name_flags
        if not bucket:
            raise ValueError("SUPABASE_BUCKET_NAME_FLAGS is not set")

        for rest_country in rest_countries:
            # Convert to CountryData (validates and extracts required fields)
            country = rest_country.to_country_data()

            # Upload flag to storage, fallback to original URL on error
            original_flag_url = country.flag_url
            try:
                flag_url = self._upload_flag_to_storage(country.flag_url, country.iso2, bucket)
                uploaded_count += 1
            except Exception as e:
                # If upload fails (e.g., 403 Forbidden), use original URL as fallback
                print(f"[countries] Warning: Failed to upload flag for {country.iso2} ({country.name}): {e}")
                print(f"[countries] Using original URL as fallback: {original_flag_url}")
                flag_url = original_flag_url
                fallback_count += 1

            row = (
                "  ("
                + ", ".join(
                    [
                        self.format_sql_value(country.iso2),
                        self.format_sql_value(country.name),
                        self.format_sql_value(country.capital),
                        self.format_sql_value(country.continent),
                        self.format_sql_value(country.primary_language),
                        self.format_sql_value(country.primary_language_code),
                        self.format_sql_value(country.primary_currency),
                        self.format_sql_value(country.primary_currency_code),
                        self.format_sql_value(flag_url),
                    ]
                )
                + ")"
            )
            rows.append(row)

        rows.sort()

        self.write_insert_statement(
            output_path=output_path,
            table_name="public.countries",
            columns=[
                "iso2",
                "name",
                "capital",
                "continent",
                "primary_language",
                "primary_language_code",
                "primary_currency",
                "primary_currency_code",
                "flag_url",
            ],
            rows=rows,
            conflict_key="iso2",
        )

        print(f"[countries] Generated seed file: {output_path}")
        print(f"[countries] Statistics:")
        print(f"[countries]   - Total countries processed: {len(rows)}")
        print(f"[countries]   - Flags uploaded to Storage: {uploaded_count}")
        if fallback_count > 0:
            print(f"[countries]   - Flags using original URL (fallback): {fallback_count}")
