"""Supabase Storage client for uploading files and URLs."""

from pathlib import Path

import requests

from supabase import create_client, Client
from utils.settings.voyager_settings import VoyagerSeedSettings


class SupabaseStorageClient:
    """Client for uploading files to Supabase Storage."""

    def __init__(self, settings: VoyagerSeedSettings):
        """Initialize the storage client.

        Args:
            settings: Voyager seed settings containing Supabase configuration.
        """

        self.settings = settings
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
        print(f"[storage] Initialized Supabase Storage client for {settings.supabase_url}")

    def upload_from_url(
        self, url: str, bucket: str, storage_path: str, timeout: int = 30
    ) -> str:
        """Download a file from URL and upload it to Supabase Storage.

        Args:
            url: URL of the file to download.
            bucket: Name of the storage bucket.
            storage_path: Path where the file should be stored in the bucket.
            timeout: Request timeout in seconds. Defaults to 30.

        Returns:
            Public URL of the uploaded file.

        Raises:
            requests.RequestException: If downloading the file fails.
            Exception: If uploading to Supabase Storage fails.
        """
        print(f"[storage] Downloading from {url}...")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        file_content = response.content
        # Determine content type from storage path extension
        content_type = "application/octet-stream"
        if storage_path.endswith(".png"):
            content_type = "image/png"
        elif storage_path.endswith(".jpg") or storage_path.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif storage_path.endswith(".svg"):
            content_type = "image/svg+xml"

        print(f"[storage] Uploading to {bucket}/{storage_path}...")
        try:
            self.client.storage.from_(bucket).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": content_type, "upsert": "true"},
            )
        except Exception as e:
            raise Exception(f"Failed to upload   to {bucket}/{storage_path}: {e}")

        public_url = self.client.storage.from_(bucket).get_public_url(storage_path)
        print(f"[storage] Successfully uploaded to {public_url}")
        return public_url

    def upload_file(
        self, file_path: Path, bucket: str, storage_path: str
    ) -> str:
        """Upload a local file to Supabase Storage.

        Args:
            file_path: Path to the local file to upload.
            bucket: Name of the storage bucket.
            storage_path: Path where the file should be stored in the bucket.

        Returns:
            Public URL of the uploaded file.

        Raises:
            FileNotFoundError: If the local file does not exist.
            Exception: If uploading to Supabase Storage fails.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"[storage] Uploading local file {file_path} to {bucket}/{storage_path}...")

        with file_path.open("rb") as f:
            file_content = f.read()

        # Try to guess content type from extension
        content_type = "application/octet-stream"
        suffix = file_path.suffix.lower()
        if suffix == ".png":
            content_type = "image/png"
        elif suffix == ".jpg" or suffix == ".jpeg":
            content_type = "image/jpeg"
        elif suffix == ".svg":
            content_type = "image/svg+xml"

        try:
            self.client.storage.from_(bucket).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": content_type, "upsert": "true"},
            )
        except Exception as e:
            raise Exception(f"Failed to upload to {bucket}/{storage_path}: {e}")

        public_url = self.client.storage.from_(bucket).get_public_url(storage_path)
        print(f"[storage] Successfully uploaded to {public_url}")
        return public_url

