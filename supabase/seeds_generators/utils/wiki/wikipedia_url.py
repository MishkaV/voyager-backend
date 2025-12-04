"""Utility for generating Wikipedia URLs."""

from urllib.parse import quote


def generate_wikipedia_url(country_name: str) -> str:
    """Generate Wikipedia search URL for a country.

    Args:
        country_name: Name of the country.

    Returns:
        Wikipedia search URL in format: https://en.wikipedia.org/wiki/Special:Search?search=<Country>
    """
    return f"https://en.wikipedia.org/wiki/Special:Search?search={quote(country_name)}"

