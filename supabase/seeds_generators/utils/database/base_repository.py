"""Base repository class for Supabase database operations."""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from supabase import Client, create_client

from utils.settings.voyager_settings import VoyagerSeedSettings

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository class for CRUD operations on Supabase tables.

    This class provides generic CRUD methods that work with typed models.
    Subclasses should specify the model type and table name.
    """

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the repository with Supabase client.

        Args:
            settings: Voyager seed settings containing Supabase configuration.
        """
        self.settings = settings
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)

    @property
    @abstractmethod
    def _table_name(self) -> str:
        """Return the table name (with schema, e.g., 'public.countries').

        Returns:
            Table name string.
        """
        pass

    @abstractmethod
    def _model_from_dict(self, data: dict) -> T:
        """Convert a dictionary to a model instance.

        Args:
            data: Dictionary containing table row data.

        Returns:
            Model instance.
        """
        pass

    def get_all(self) -> List[T]:
        """Get all records from the table.

        Returns:
            List of model instances.
        """
        response = self.client.table(self._table_name).select("*").execute()
        return [self._model_from_dict(row) for row in response.data]

    def get_by_id(self, record_id: str) -> Optional[T]:
        """Get a record by its ID.

        Args:
            record_id: UUID string of the record.

        Returns:
            Model instance if found, None otherwise.
        """
        response = (
            self.client.table(self._table_name)
            .select("*")
            .eq("id", record_id)
            .execute()
        )
        if response.data:
            return self._model_from_dict(response.data[0])
        return None

    def insert(self, record: T) -> T:
        """Insert a single record into the table.

        Args:
            record: Model instance to insert.

        Returns:
            Inserted model instance with generated ID.
        """
        data = self._record_to_dict(record)
        response = self.client.table(self._table_name).insert(data).execute()
        if response.data:
            return self._model_from_dict(response.data[0])
        raise ValueError(f"Failed to insert record into {self._table_name}")

    def insert_many(self, records: List[T]) -> List[T]:
        """Insert multiple records into the table.

        Args:
            records: List of model instances to insert.

        Returns:
            List of inserted model instances with generated IDs.
        """
        if not records:
            return []
        data = [self._record_to_dict(record) for record in records]
        response = self.client.table(self._table_name).insert(data).execute()
        return [self._model_from_dict(row) for row in response.data]

    def update(self, record: T) -> T:
        """Update a record in the table.

        Args:
            record: Model instance with updated data.

        Returns:
            Updated model instance.
        """
        data = self._record_to_dict(record)
        # Extract ID for the update query
        record_id = data.get("id")
        if not record_id:
            raise ValueError(f"Record must have an 'id' field to update")

        response = (
            self.client.table(self._table_name)
            .update(data)
            .eq("id", record_id)
            .execute()
        )
        if response.data:
            return self._model_from_dict(response.data[0])
        raise ValueError(f"Failed to update record in {self._table_name}")

    def delete(self, record_id: str) -> bool:
        """Delete a record from the table.

        Args:
            record_id: UUID string of the record to delete.

        Returns:
            True if deleted successfully, False otherwise.
        """
        response = (
            self.client.table(self._table_name)
            .delete()
            .eq("id", record_id)
            .execute()
        )
        return response.data is not None

    def _record_to_dict(self, record: T) -> dict:
        """Convert a model instance to a dictionary for database operations.

        Args:
            record: Model instance.

        Returns:
            Dictionary representation of the model.
        """
        if hasattr(record, "__dataclass_fields__"):
            # Handle dataclass
            from dataclasses import asdict

            data = asdict(record)
            # Remove empty string IDs - database will generate UUID automatically
            if "id" in data and data["id"] == "":
                del data["id"]
            return data
        elif hasattr(record, "__dict__"):
            data = {k: v for k, v in record.__dict__.items() if v is not None}
            # Remove empty string IDs - database will generate UUID automatically
            if "id" in data and data["id"] == "":
                del data["id"]
            return data
        else:
            raise ValueError(f"Cannot convert {type(record)} to dict")

