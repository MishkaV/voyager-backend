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

from countries_generator import CountriesGenerator
from utils.settings.voyager_settings import VoyagerSeedSettings

def main():
    """Main entry point for generating all seed files."""
    settings = VoyagerSeedSettings()

    supabase_root = Path(__file__).resolve().parents[1]
    seeds_dir = supabase_root / settings.seeds_output_dir_name
    seeds_dir.mkdir(parents=True, exist_ok=True)
    print(f"[generator] Output directory: {seeds_dir}")

    generators = [
        CountriesGenerator(settings),
        # Add more generators here as they are created
    ]

    print(f"[generator] Starting generation of {len(generators)} seed file(s)...")

    for generator in generators:
        seed_path = seeds_dir / generator.filename
        generator_name = generator.__class__.__name__.replace("Generator", "").lower()
        print(f"[generator] Generating {generator_name} seed → {seed_path}")
        try:
            generator.generate(seed_path)
            print(f"[generator] ✓ {generator_name} seed generated successfully\n")
        except Exception as e:
            print(f"[generator] ✗ Failed to generate {generator_name} seed: {e}")
            raise

    print("[generator] All seed files generated successfully!")


if __name__ == "__main__":
    main()
