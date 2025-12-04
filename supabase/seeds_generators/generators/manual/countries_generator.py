"""Generate countries seed SQL file from RestCountries API."""

import dataclasses
from pathlib import Path
from typing import List

from seeds_generators.generators.base_generator import BaseGenerator
from utils.palette.color_extractor import ColorExtractor
from utils.restcountries.client import RestCountriesClient
from utils.restcountries.models import RestCountryResponse
from utils.settings.voyager_settings import VoyagerSeedSettings
from utils.storage.supabase_storage import SupabaseStorageClient


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
    flag_full_path: str  # Full path in format "bucket/path" after upload
    background_hex: str  # ARGB hex color with 80% alpha


class CountriesGenerator(BaseGenerator):
    """Generator for countries seed SQL file."""

    filename = "03_countries.sql"
    
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
        self.restcountries_client: RestCountriesClient = RestCountriesClient(self.settings)
        self.storage_client: SupabaseStorageClient = SupabaseStorageClient(self.settings)
        self.color_extractor: ColorExtractor = ColorExtractor()
        print(
            f"[countries] Storage client initialized, will upload flags to {self.settings.supabase_bucket_name_flags}"
        )

    def _upload_flag_to_storage(self, flag_url: str, iso2: str, bucket: str) -> str:
        """Upload country flag to Supabase Storage (only if not exists).

        Args:
            flag_url: Original flag URL from RestCountries API.
            iso2: Country ISO2 code (e.g., "US").
            bucket: Storage bucket name.

        Returns:
            Full path in format "{bucket}/{storage_path}" (e.g., "flags/US.png").

        Raises:
            ValueError: If flag URL is empty or upload fails.
        """
        if not flag_url:
            raise ValueError(f"Flag URL cannot be empty for country {iso2}")

        storage_path = f"{iso2}.png"
        return self.storage_client.get_or_upload_from_url(flag_url, bucket, storage_path)

    def generate(self, output_path: Path) -> None:
        """Generate countries seed SQL file.

        Args:
            output_path: Path where the SQL file should be written.

        Raises:
            ValueError: If required country data is missing.
            Exception: If flag upload fails.
        """
        # Fetch all countries from API
        all_countries = self.restcountries_client.get_all_countries()
        
        # Filter out ignored countries
        rest_countries: List[RestCountryResponse] = []
        ignored_count = 0
        for country in all_countries:
            # Skip ignored countries by ISO2 code
            cca2 = country.cca2.upper()
            if cca2 in self.IGNORED_COUNTRIES:
                ignored_count += 1
                print(f"[countries] Ignoring country: {cca2} ({country.name.common})")
                continue
            
            # Skip countries in ignored continents
            if any(continent in self.IGNORED_CONTINENTS for continent in country.continents):
                ignored_count += 1
                print(f"[countries] Ignoring country in ignored continent: {cca2} ({country.name.common})")
                continue
            
            rest_countries.append(country)
        
        print(f"[countries] Filtered {len(rest_countries)} countries (ignored {ignored_count})")

        rows: List[str] = []
        uploaded_count = 0

        print(f"[countries] Processing {len(rest_countries)} countries...")

        bucket = self.settings.supabase_bucket_name_flags
        if not bucket:
            raise ValueError("SUPABASE_BUCKET_NAME_FLAGS is not set")

        for rest_country in rest_countries:
            # Convert to CountryData (validates and extracts required fields)
            country = rest_country.to_country_data(CountryData)

            # Get original flag URL from API response
            original_flag_url = rest_country.flags.png or rest_country.flags.svg

            # Upload flag to storage
            try:
                flag_full_path = self._upload_flag_to_storage(original_flag_url, country.iso2, bucket)
                if not flag_full_path:
                    raise ValueError(f"Flag full path cannot be empty for country {country.iso2}")
                country.flag_full_path = flag_full_path
                uploaded_count += 1
            except Exception as e:
                # If upload fails, raise error (no fallback since flag_full_path is required)
                raise Exception(
                    f"Failed to upload flag for {country.iso2} ({country.name}): {e}. "
                    f"Flag full path is required and cannot be empty."
                )

            # Extract color palette from flag image
            try:
                # Get signed URL for palette extraction (more reliable than public URL)
                signed_url = self.storage_client.get_signed_url(bucket, f"{country.iso2}.png")
                
                # Extract palette and get muted color with 80% alpha
                palette = self.color_extractor.extract_palette_from_url(signed_url)
                background_hex = self.color_extractor.get_muted_color_with_alpha(palette, alpha_percent=80)
                if not background_hex:
                    raise ValueError("Background hex cannot be empty")
                country.background_hex = background_hex
                print(f"[countries] Extracted palette for {country.iso2}: {background_hex}")
            except Exception as e:
                # If palette extraction fails, raise error (background_hex is required)
                raise Exception(
                    f"Failed to extract palette for {country.iso2} ({country.name}): {e}. "
                    f"Background hex is required and cannot be empty."
                )

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
                        self.format_sql_value(country.flag_full_path),
                        self.format_sql_value(country.background_hex),
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
                "flag_full_patch",
                "background_hex",
            ],
            rows=rows,
            conflict_key="iso2",
        )

        print(f"[countries] Generated seed file: {output_path}")
        print(f"[countries] Statistics:")
        print(f"[countries]   - Total countries processed: {len(rows)}")
        print(f"[countries]   - Flags uploaded to Storage: {uploaded_count}")
