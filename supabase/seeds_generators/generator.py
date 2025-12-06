"""
Entry point to generate all seed SQL files.

Usage:
  cd supabase
  python seeds_generators/generator.py
"""

from pathlib import Path
from dotenv import load_dotenv

# Load .env from seeds_generators directory BEFORE importing modules that use settings
seeds_generators_dir = Path(__file__).resolve().parent
env_path = seeds_generators_dir / '.env'
load_dotenv(env_path)

from generators.llm.vibes_country_generator import VibesCountryGenerator
from generators.llm.country_best_time_generator import CountryBestTimeGenerator
from generators.llm.country_overview_generator import CountryOverviewGenerator
from generators.llm.country_specific_ai_suggest_generator import CountrySpecificAISuggestGenerator
from generators.llm.general_ai_suggest_generator import GeneralAISuggestGenerator
from generators.llm.podcast_script_generator import PodcastScriptGenerator
from generators.llm.podcast_audio_generator import PodcastAudioGenerator
from generators.manual.countries_generator import CountriesGenerator
from utils.settings.voyager_settings import VoyagerSeedSettings

def main():
    """Main entry point for generating all seed files."""
    settings = VoyagerSeedSettings()

    supabase_root = Path(__file__).resolve().parents[1]
    seeds_dir = supabase_root / settings.seeds_output_dir_name
    seeds_dir.mkdir(parents=True, exist_ok=True)
    print(f"[generator] Output directory: {seeds_dir}")

    generators = [
        # Base manual
        # CountriesGenerator(settings),
        # LLM-based (writes directly to database)
        # VibesCountryGenerator(settings),
        # CountryBestTimeGenerator(settings),
        # CountryOverviewGenerator(settings),
        # GeneralAISuggestGenerator(settings),
        # CountrySpecificAISuggestGenerator(settings),
        # PodcastScriptGenerator(settings),
        PodcastAudioGenerator(settings),
    ]

    print(f"[generator] Starting generation of {len(generators)} seed file(s)...")

    for generator in generators:
        generator_name = generator.__class__.__name__.replace("Generator", "").lower()
        
        # LLM generators don't create SQL files, they write directly to database
        if generator.filename:
            seed_path = seeds_dir / generator.filename
            print(f"[generator] Generating {generator_name} seed → {seed_path}")
        else:
            seed_path = Path()  # Dummy path for LLM generators
            print(f"[generator] Generating {generator_name} (writing directly to database)")
        
        try:
            generator.generate(seed_path)
            print(f"[generator] ✓ {generator_name} seed generated successfully\n")
        except Exception as e:
            print(f"[generator] ✗ Failed to generate {generator_name} seed: {e}")
            raise

    print("[generator] All seed files generated successfully!")


if __name__ == "__main__":
    main()
