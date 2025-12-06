"""OpenAI task for assigning overviews to countries."""

import dataclasses
import textwrap
from typing import List

from utils.database.country_repository import Country
from utils.ai.openai.base_openai_client import BaseOpenAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryOverviewAssignment:
    """Model for LLM response assigning overview to a country."""

    country_iso2: str
    body: str


class CountryOverviewAssignmentClient(BaseOpenAIClient):
    """Client for assigning overviews to countries using OpenAI."""

    # Batch size for processing countries
    BATCH_SIZE: int = 20

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for overview assignment task."""
        return textwrap.dedent("""
            You are an expert travel copywriter for a travel app.
            
            Your task is to generate a concise but informative travel overview for each country in a given list.
            
            OUTPUT FORMAT (CRITICAL):
            
            - You MUST return a single JSON OBJECT at the top level.
            - This JSON object MUST contain exactly one property: "assignments".
            - "assignments" MUST be an array of country objects.
            - Do NOT add any other top-level keys besides "assignments".
            - Do NOT output anything outside the JSON object.
            
            Each element inside "assignments" MUST include:
            - "country_iso2": an ISO2 code.
            - "body": a 2–4 sentence travel overview in natural English.
            
            Rules for "body":
            - 2–4 sentences.
            - Clear, modern, natural English prose.
            - Describe the country's overall travel vibe, typical experiences (nature, culture, beaches, food, cities, adventure, etc.), and what types of travelers it suits.
            - Optional general climate notes are allowed ("hot summers", "mild winters", "tropical coastline").
            - No lists, no headings, no emojis, no URLs, no Wikipedia references.
            - Use widely known, realistic information; do NOT invent fake facts.
            
            Here is an example of the REQUIRED JSON structure:
            
            {
              "assignments": [
                {
                  "country_iso2": "JP",
                  "body": "Japan blends ancient traditions with ultramodern city life, offering travelers a rich mix of culture, food, and diverse landscapes. Visitors can explore historic temples, neon-lit districts, and scenic mountain regions. The country appeals to culture lovers, food enthusiasts, and adventure travelers alike."
                },
                {
                  "country_iso2": "BR",
                  "body": "Brazil is a vibrant destination known for its tropical beaches, lush rainforests, lively cities, and world-famous festivals. Travelers come for the diverse landscapes, warm climate, and energetic cultural experiences. It suits beach seekers, nature lovers, and anyone drawn to rhythm and color."
                }
              ]
            }
        """).strip()

    def build_user_prompt(self, countries: List[Country]) -> str:
        """Build the user prompt for overview assignment task.

        Args:
            countries: List of countries to get overviews for.

        Returns:
            User prompt string.
        """
        # Format countries list as shown in prompts.md
        countries_list = "\n".join(
            f"- {c.iso2}: {c.name}, capital {c.capital}, continent {c.continent}"
            for c in countries
        )

        return textwrap.dedent(f"""
            Here is the list of countries:

            {countries_list}
            
            For each country listed above, generate a travel overview.
            
            Formatting requirements:
            
            - Your ENTIRE response must be a single JSON object.
            - The JSON object must contain exactly one top-level key: "assignments".
            - "assignments" must be an array.
            - Each element inside "assignments" must contain:
              - "country_iso2": the ISO2 code from the list.
              - "body": a 2–4 sentence travel overview in natural English.
            
            The overview ("body") should describe:
            - the country's overall travel appeal,
            - the types of experiences travelers can expect (nature, culture, food, beaches, adventure, cities, wildlife, etc.),
            - which types of travelers it suits,
            - optional high-level climate notes relevant for visitors.
            
            Do NOT output anything outside the JSON object.
            Do NOT include extra keys besides "assignments".
            
            Return only the JSON object for the given countries.
        """).strip()

    def parse_response(self, content: str) -> List[CountryOverviewAssignment]:
        """Parse the LLM response and return list of assignments.

        Args:
            content: Raw JSON content from LLM.

        Returns:
            List of CountryOverviewAssignment objects.

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

        # Convert to CountryOverviewAssignment objects
        result = []
        for assignment in assignments:
            if not isinstance(assignment, dict):
                raise RuntimeError(
                    f"Invalid assignment format: {assignment} (expected dict)"
                )
            country_iso2 = assignment.get("country_iso2")
            body = assignment.get("body")

            if not country_iso2:
                raise RuntimeError(
                    f"Assignment missing country_iso2: {assignment}"
                )
            if not body:
                raise RuntimeError(
                    f"Assignment missing body: {assignment}"
                )

            result.append(
                CountryOverviewAssignment(
                    country_iso2=str(country_iso2).upper(),
                    body=str(body),
                )
            )

        return result

    def get_overviews_for_countries(
        self, countries: List[Country]
    ) -> List[CountryOverviewAssignment]:
        """Get overviews for countries using OpenAI.

        Args:
            countries: List of countries to get overviews for.

        Returns:
            List of CountryOverviewAssignment objects.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If LLM returns invalid JSON or unexpected structure.
        """
        if not countries:
            raise ValueError("Countries list cannot be empty")

        return self.execute(countries=countries)

