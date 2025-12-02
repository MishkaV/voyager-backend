# Seed Generators

This directory contains Python scripts that generate SQL seed files for the Voyager Supabase database.

## Overview

The seed generators fetch data from external APIs (like RestCountries) and generate SQL INSERT statements that can be used to populate the database with initial data.

## Structure

```
seeds_generators/
├── generator.py              # Main entry point - generates all seed files
├── countries_generator.py    # Generates countries seed from RestCountries API
├── requirements.txt          # Python dependencies for this module
├── .env.example              # Example environment variables configuration
├── README.md                 # This file
└── utils/
    └── settings/
        ├── base_settings.py      # Base settings utility
        └── voyager_settings.py   # Voyager-specific settings configuration
```

## Setup

### 1. Create Virtual Environment (Recommended)

It's recommended to use a virtual environment to isolate dependencies:

```bash
cd supabase/seeds_generators

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

Install the required Python packages from this module's `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file to the `supabase/` directory and fill in the required values:

```bash
cp supabase/seeds_generators/.env.example supabase/.env
```

Edit `supabase/.env` and set the **required** variables.

**Note**: If you're using a virtual environment, make sure it's activated before running the generators.

## Usage

### Generate All Seed Files

From the `supabase` directory, run:

```bash
python seeds_generators/generator.py
```

This will:
1. Load environment variables from `supabase/.env` (if present)
2. Generate all seed SQL files in the `seeds/` directory (or `SEEDS_OUTPUT_DIR` if specified)

### Generate Individual Seed Files

You can also run individual generators directly:

```bash
# Generate countries seed
python seeds_generators/countries_generator.py
```