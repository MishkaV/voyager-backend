"""Voyager seed generation settings configuration."""

import dataclasses

from utils.settings.base_settings import BaseSettings


@dataclasses.dataclass
class VoyagerSeedSettings(BaseSettings):
    """Settings for Voyager seed file generation.
    
    Configuration for RestCountries API, seed output directory, and Supabase.
    All settings can be configured via environment variables.
    """

    # RestCountries config
    # RestCountries API base URL
    restcountries_base_url: str = BaseSettings._str_from_environ(
        "RESTCOUNTRIES_BASE_URL",
        "https://restcountries.com/v3.1",
    )

    # Supabase config
    # Supabase project URL
    supabase_url: str = BaseSettings._str_from_environ("SUPABASE_URL")
    # Supabase service role API key
    supabase_key: str = BaseSettings._str_from_environ("SUPABASE_KEY")

    # Supabase storage bucket name for country flag images
    supabase_bucket_name_flags: str = BaseSettings._str_from_environ(
        "SUPABASE_BUCKET_NAME_FLAGS",
        "flags",
    )

    # General settings
    # Directory name (relative to supabase root) for seed SQL files
    seeds_output_dir_name: str = BaseSettings._str_from_environ(
        "SEEDS_OUTPUT_DIR",
        "seeds",
    )
