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

    def file_exists(self, bucket: str, storage_path: str) -> bool:
        """Check if a file exists in Supabase Storage bucket.

        Args:
            bucket: Name of the storage bucket.
            storage_path: Path to the file in the bucket.

        Returns:
            True if the file exists, False otherwise.
        """
        try:
            # Try to list files at the path
            files = self.client.storage.from_(bucket).list(path=storage_path)
            # If we get a response, check if it's a direct match
            if isinstance(files, list) and len(files) > 0:
                return True
            # Try downloading to check existence (more reliable)
            self.client.storage.from_(bucket).download(storage_path)
            return True
        except Exception:
            # File doesn't exist or we don't have access
            return False

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
            Full path in format "{bucket}/{storage_path}".

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
            raise Exception(f"Failed to upload to {bucket}/{storage_path}: {e}")

        full_path = f"{bucket}/{storage_path}"
        print(f"[storage] Successfully uploaded to {full_path}")
        return full_path

    def upload_file(
        self, file_path: Path, bucket: str, storage_path: str
    ) -> str:
        """Upload a local file to Supabase Storage.

        Args:
            file_path: Path to the local file to upload.
            bucket: Name of the storage bucket.
            storage_path: Path where the file should be stored in the bucket.

        Returns:
            Full path in format "{bucket}/{storage_path}".

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

        full_path = f"{bucket}/{storage_path}"
        print(f"[storage] Successfully uploaded to {full_path}")
        return full_path

    def get_or_upload_from_url(
        self, url: str, bucket: str, storage_path: str, timeout: int = 30
    ) -> str:
        """Check if file exists in storage, upload from URL only if it doesn't exist.

        Args:
            url: URL of the file to download (if needed).
            bucket: Name of the storage bucket.
            storage_path: Path where the file should be stored in the bucket.
            timeout: Request timeout in seconds. Defaults to 30.

        Returns:
            Full path in format "{bucket}/{storage_path}".

        Raises:
            requests.RequestException: If downloading the file fails.
            Exception: If uploading to Supabase Storage fails.
        """
        # Check if file already exists
        if self.file_exists(bucket, storage_path):
            full_path = f"{bucket}/{storage_path}"
            print(f"[storage] File already exists: {full_path}, skipping upload")
            return full_path
        
        # File doesn't exist, upload it
        return self.upload_from_url(url, bucket, storage_path, timeout)

    def get_signed_url(self, bucket: str, storage_path: str, expires_in: int = 3600) -> str:
        """Get a signed URL for accessing a file in Supabase Storage.

        Args:
            bucket: Name of the storage bucket.
            storage_path: Path to the file in the bucket.
            expires_in: URL expiration time in seconds. Defaults to 3600 (1 hour).

        Returns:
            Signed URL string for accessing the file.

        Raises:
            Exception: If creating the signed URL fails.
        """
        try:
            result = self.client.storage.from_(bucket).create_signed_url(
                path=storage_path,
                expires_in=expires_in,
            )
            # Supabase client may return dict with 'signedURL' key or just a string
            if isinstance(result, dict):
                signed_url = result.get('signedURL') or result.get('signedUrl')
                if not signed_url:
                    raise Exception(f"Invalid signed URL response format: {result}")
                return signed_url
            elif isinstance(result, str):
                return result
            else:
                raise Exception(f"Unexpected signed URL response type: {type(result)}")
        except Exception as e:
            raise Exception(f"Failed to create signed URL for {bucket}/{storage_path}: {e}")

