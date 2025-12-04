"""Base generator class for seed SQL file generation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from utils.settings.voyager_settings import VoyagerSeedSettings


class BaseGenerator(ABC):
    """Base class for seed SQL file generators."""

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the generator.

        Args:
            settings: Voyager seed settings for configuration.
        """
        self.settings = settings

    @property
    def filename(self) -> str | None:
        """Return the output filename for this generator.

        Returns:
            Filename (e.g., "03_countries.sql") or None if generator doesn't create SQL files.
        """
        return None

    @staticmethod
    def sql_escape(value: str) -> str:
        """Escape single quotes for SQL string literals.

        Args:
            value: String value to escape.

        Returns:
            Escaped string safe for SQL.
        """
        return value.replace("'", "''")

    @staticmethod
    def format_sql_value(value: str) -> str:
        """Format a value for SQL INSERT statement.

        Args:
            value: Value to format.

        Returns:
            Formatted SQL value string.
        """
        return f"'{BaseGenerator.sql_escape(value)}'"

    def write_insert_statement(
        self,
        output_path: Path,
        table_name: str,
        columns: List[str],
        rows: List[str],
        conflict_key: str,
        update_columns: Optional[List[str]] = None,
    ) -> None:
        """Write SQL INSERT statement with ON CONFLICT clause.

        Args:
            output_path: Path where the SQL file should be written.
            table_name: Name of the table (with schema, e.g., "public.countries").
            columns: List of column names.
            rows: List of formatted row values (already escaped and formatted).
            conflict_key: Column name for ON CONFLICT clause.
            update_columns: List of columns to update on conflict. If None, updates all columns except conflict_key.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if update_columns is None:
            # Update all columns except the conflict key
            update_columns = [col for col in columns if col != conflict_key]

        with output_path.open("w", encoding="utf-8") as f:
            f.write(
                f"-- THIS FILE IS GENERATED. Edit seeds_generators/{self.__class__.__name__.lower()}.py instead of this file.\n"
            )
            f.write(f"insert into {table_name} (\n")
            f.write("  " + ",\n  ".join(columns) + "\n")
            f.write(") values\n")
            f.write(",\n".join(rows))
            f.write("\n")
            f.write(f"on conflict ({conflict_key}) do update set\n")
            f.write("  " + ",\n  ".join(f"{col} = excluded.{col}" for col in update_columns))
            f.write(";\n")

    @abstractmethod
    def generate(self, output_path: Path) -> None:
        """Generate the seed SQL file.

        This method must be implemented by subclasses.

        Args:
            output_path: Path where the SQL file should be written.
        """
        pass

