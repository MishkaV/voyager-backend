# Voyager Supabase

Repository for storing configuration and database migrations for the Voyager project using Supabase.

## Project Structure

```
voyager-supabase/
├── supabase/
│   ├── config.toml          # Local Supabase configuration
│   └── migrations/          # SQL database migrations
│       └── 20251130142812_remote_schema.sql
└── README.md
```

## Quick Start

### Requirements

- [Supabase CLI](https://supabase.com/docs/guides/cli) installed locally

### Running Local Environment

```bash
# Start local Supabase
supabase start

# Apply migrations to local database
supabase db push

# Stop local Supabase
supabase stop
```

## Useful Links

- [Supabase CLI Documentation](https://supabase.com/docs/guides/cli)
- [Supabase Documentation](https://supabase.com/docs)
