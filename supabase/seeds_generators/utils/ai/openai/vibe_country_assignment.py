"""OpenAI task for assigning vibes to countries."""

import dataclasses
import textwrap
from typing import List

from utils.database.country_repository import Country
from utils.database.vibe_repository import Vibe
from utils.ai.openai.base_openai_client import BaseOpenAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class VibeCountryAssignment:
    """Model for LLM response assigning vibes to a country."""

    country_iso2: str
    vibe_titles: List[str]


class VibeCountryAssignmentClient(BaseOpenAIClient):
    """Client for assigning vibes to countries using OpenAI."""

    # Batch size for processing countries
    BATCH_SIZE: int = 20

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for vibe assignment task."""
        return textwrap.dedent("""
            You assign the most fitting vibes (atmospheres) to countries.
            Your goal is to match each country with 3–5 vibes from a predefined list.
            
            Rules:
            - Use ONLY the vibe titles provided in the list.
            - Do NOT invent your own vibes.
            - Select 3 to 5 vibes per country.
            - Make meaningful, logical assignments based on geography, culture, climate, and stereotypes.
            - Output STRICT JSON only. No comments, no explanations.
        """).strip()

    def build_user_prompt(self, vibes: List[Vibe], countries: List[Country]) -> str:
        """Build the user prompt for vibe assignment task.

        Args:
            vibes: List of all available vibes.
            countries: List of countries to assign vibes to.

        Returns:
            User prompt string.
        """
        vibes_desc = "\n".join(
            f'- "{v.title}" ({v.icon_emoji})' for v in vibes
        )

        countries_desc = "\n".join(
            f'- {c.iso2}: {c.name}, capital {c.capital}, continent {c.continent}, primary_language {c.primary_language}'
            for c in countries
        )

        return textwrap.dedent(f"""
            Here is the list of available vibes (title + emoji):
            {vibes_desc}
            
            Here is the list of countries to annotate:
            {countries_desc}
            
            For each country, choose 3–5 vibes that best match the country's atmosphere,
            culture, geography, lifestyle, or global perception.
            
            Output format (strict JSON object with "assignments" array):
            
            {{
              "assignments": [
                {{
                  "country_iso2": "BR",
                  "vibe_titles": ["Beach", "Party", "Nature"]
                }},
                {{
                  "country_iso2": "JP",
                  "vibe_titles": ["Technology", "Urban", "Culture"]
                }}
              ]
            }}
        """).strip()

    def parse_response(self, content: str) -> List[VibeCountryAssignment]:
        """Parse the LLM response and return list of assignments.

        Args:
            content: Raw JSON content from LLM.

        Returns:
            List of VibeCountryAssignment objects.

        Raises:
            RuntimeError: If response cannot be parsed.
        """
        parsed = self._parse_json(content)

        # Handle different response formats
        if isinstance(parsed, list):
            assignments = parsed
        elif isinstance(parsed, dict) and "data" in parsed:
            assignments = parsed["data"]
        elif isinstance(parsed, dict) and "assignments" in parsed:
            assignments = parsed["assignments"]
        else:
            raise RuntimeError(f"Unexpected JSON structure: {parsed}")

        # Convert to VibeCountryAssignment objects
        result = []
        for assignment in assignments:
            if not isinstance(assignment, dict):
                raise RuntimeError(
                    f"Invalid assignment format: {assignment} (expected dict)"
                )
            country_iso2 = assignment.get("country_iso2")
            vibe_titles = assignment.get("vibe_titles", [])

            if not country_iso2:
                raise RuntimeError(
                    f"Assignment missing country_iso2: {assignment}"
                )
            if not isinstance(vibe_titles, list):
                raise RuntimeError(
                    f"Assignment vibe_titles must be a list: {assignment}"
                )

            result.append(
                VibeCountryAssignment(
                    country_iso2=str(country_iso2).upper(),
                    vibe_titles=[str(title) for title in vibe_titles],
                )
            )

        return result

    def assign_vibes_to_countries(
            self, vibes: List[Vibe], countries: List[Country]
    ) -> List[VibeCountryAssignment]:
        """Assign vibes to countries using OpenAI.

        Args:
            vibes: List of all available vibes.
            countries: List of countries to assign vibes to.

        Returns:
            List of VibeCountryAssignment objects.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If LLM returns invalid JSON or unexpected structure.
        """
        if not vibes:
            raise ValueError("Vibes list cannot be empty")
        if not countries:
            raise ValueError("Countries list cannot be empty")

        return self.execute(vibes=vibes, countries=countries)
