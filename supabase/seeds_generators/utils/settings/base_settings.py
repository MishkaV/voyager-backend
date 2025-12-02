"""Base settings utility for environment variable handling."""

import dataclasses
import os

@dataclasses.dataclass
class BaseSettings:
    """Base class for settings that read configuration from environment variables."""
    
    @staticmethod
    def _str_from_environ(environ_key: str, default_value: str | None = None) -> str:
        """Read a string value from environment variables.
        
        Args:
            environ_key: The name of the environment variable to read.
            default_value: Optional default value. If None and environment variable is not set, raises ValueError.
        
        Returns:
            Stripped string value or default if not set.
        
        Raises:
            ValueError: If environment variable is not set and default_value is None.
        """
        value = os.environ.get(environ_key)
        
        if value is not None:
            return str(value).strip()
        
        if default_value is not None:
            return str(default_value).strip()
        
        raise ValueError(
            f"Environment variable '{environ_key}' is not set and no default value provided"
        )

    @staticmethod
    def _int_from_environ(environ_key: str, default_value: int) -> int:
        """Read an integer value from environment variables.
        
        Args:
            environ_key: The name of the environment variable to read.
            default_value: Default value if not set.
        
        Returns:
            Integer value or default if not set.
        
        Raises:
            ValueError: If value cannot be converted to integer.
        """
        return int(os.environ.get(environ_key, default_value))

    @staticmethod
    def _float_from_environ(environ_key: str, default_value: float) -> float:
        """Read a float value from environment variables.
        
        Args:
            environ_key: The name of the environment variable to read.
            default_value: Default value if not set.
        
        Returns:
            Float value or default if not set.
        
        Raises:
            ValueError: If value cannot be converted to float.
        """
        return float(os.environ.get(environ_key, default_value))

    @staticmethod
    def _bool_from_environ(environ_key: str, default_value: bool) -> bool:
        """Read a boolean value from environment variables.
        
        True if value matches (case-insensitive): "true", "1", "t", or "y".
        
        Args:
            environ_key: The name of the environment variable to read.
            default_value: Default value if not set.
        
        Returns:
            Boolean value or default if not set.
        """
        return str(os.environ.get(environ_key, str(default_value))).strip().lower() in ("true", "1", "t", "y")