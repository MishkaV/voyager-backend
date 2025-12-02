#!/bin/bash

# Script to update Supabase migrations and commit changes
# Usage: ./scripts/update-migrations.sh [migration-prefix]
# If migration-prefix is provided, uses -f flag; otherwise runs without it

set -e

# Get the migration prefix from command line argument (optional)
PREFIX="$1"

# Run supabase db diff
if [ -n "$PREFIX" ]; then
  echo "Generating migration with prefix: $PREFIX"
  supabase db diff -f "$PREFIX" --linked
else
  echo "Generating migration without prefix"
  supabase db diff --linked
fi

# Stage all changes
echo "Staging all changes..."
git add *

# Commit with message
echo "Committing changes..."
git commit -m "Update migrations"

# Push to remote
echo "Pushing to remote repository..."
git push

echo "Migration update completed successfully!"




