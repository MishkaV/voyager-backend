"""Color palette extractor using vibrant-python library."""

from io import BytesIO
from typing import Optional

import requests
from vibrant import Vibrant


class ColorExtractor:
    """Extract color palettes from images using vibrant-python."""

    DEFAULT_COLOR = "#CC000000"  # Black with 80% alpha as fallback

    def __init__(self):
        """Initialize the color extractor."""
        self.vibrant = Vibrant()

    def extract_palette_from_url(self, url: str, timeout: int = 30) -> Optional[dict]:
        """Extract color palette from an image URL.

        Args:
            url: URL of the image to analyze.
            timeout: Request timeout in seconds. Defaults to 30.

        Returns:
            Dictionary with vibrant palette colors, or None if extraction fails.

        Raises:
            requests.RequestException: If downloading the image fails.
        """
        try:
            # Download the image
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            # Extract palette using instance vibrant
            palette = self.vibrant.get_palette(BytesIO(response.content))

            return palette
        except Exception as e:
            print(f"[color_extractor] Failed to extract palette from {url}: {e}")
            return None

    def get_muted_color_with_alpha(
        self, palette: Optional[dict], alpha_percent: int = 80
    ) -> str:
        """Get muted color from palette with alpha channel in ARGB format.

        Args:
            palette: Vibrant palette dictionary (from extract_palette_from_url).
            alpha_percent: Alpha transparency percentage (0-100). Defaults to 80.

        Returns:
            Hex color string in ARGB format (e.g., "#CCFFFFFF" for 80% alpha).
            Returns default color "#CC000000" if palette is None or muted color is unavailable.
        """
        if palette is None:
            return self.DEFAULT_COLOR

        # Try to get muted color, fallback to dark_muted
        muted_color = palette.muted or palette.dark_muted

        if muted_color is None:
            print("[color_extractor] No muted color available in palette, using default")
            return self.DEFAULT_COLOR

        try:
            # Get RGB values
            rgb = muted_color.rgb

            # Convert alpha percentage to hex (0-100 -> 0-255 -> 00-FF)
            alpha_value = int((alpha_percent / 100.0) * 255)
            alpha_hex = f"{alpha_value:02X}"

            # Convert RGB to hex (ARGB format)
            r_hex = f"{rgb[0]:02X}"
            g_hex = f"{rgb[1]:02X}"
            b_hex = f"{rgb[2]:02X}"

            argb_color = f"#{alpha_hex}{r_hex}{g_hex}{b_hex}"
            return argb_color

        except Exception as e:
            print(f"[color_extractor] Failed to convert color to ARGB: {e}")
            return self.DEFAULT_COLOR

