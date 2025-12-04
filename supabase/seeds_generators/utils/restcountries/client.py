"""Client for RestCountries API."""

import dataclasses
from typing import Dict, List

import requests

from models import Currency, Flags, Name, RestCountryResponse
from seeds_generators.utils.settings.voyager_settings import VoyagerSeedSettings


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


class RestCountriesClient:
    """Client for fetching country data from RestCountries API."""

    RESTCOUNTRIES_FIELDS = "cca2,name,capital,continents,languages,currencies,flags"

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the RestCountries client.
        
        Args:
            settings: Voyager seed settings containing API configuration.
        """
        self.settings = settings

    def get_all_countries(self) -> List[RestCountryResponse]:
        """Fetch all countries from RestCountries API.

        Returns:
            List of RestCountryResponse objects with parsed country data.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"{self.settings.restcountries_base_url}/all"
        params = {"fields": self.RESTCOUNTRIES_FIELDS}

        print(f"[restcountries] Fetching countries from {url}...")

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        print(f"[restcountries] Fetched {len(data)} countries from API")

        countries: List[RestCountryResponse] = []
        for country_dict in data:
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

        print(f"[restcountries] Parsed {len(countries)} countries")
        return countries
