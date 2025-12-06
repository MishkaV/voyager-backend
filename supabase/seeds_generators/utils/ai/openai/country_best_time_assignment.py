"""OpenAI task for assigning best times to countries."""

import dataclasses
import textwrap
from typing import Dict, List

from utils.database.country_repository import Country
from utils.ai.openai.base_openai_client import BaseOpenAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryBestTimeAssignment:
    """Model for LLM response assigning best times to a country."""

    country_iso2: str
    best_times: List[Dict[str, str]]


class CountryBestTimeAssignmentClient(BaseOpenAIClient):
    """Client for assigning best times to countries using OpenAI."""

    # Batch size for processing countries
    BATCH_SIZE: int = 20

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for best times assignment task."""
        return textwrap.dedent("""
            You are an expert travel advisor.  
            Your task is to generate the best 2–5 times of the year to visit each country in a given list.
            
            OUTPUT FORMAT (CRITICAL):
            
            - You MUST return a single JSON OBJECT at the top level.
            - This JSON object MUST have exactly one property: "assignments".
            - "assignments" MUST be an array of country objects.
            - Do NOT add any other top-level keys besides "assignments".
            - Do NOT add any explanations, comments, or text outside the JSON.
            
            The structure MUST be:
            
            {
              "assignments": [
                {
                  "country_iso2": "XX",
                  "best_times": [
                    {
                      "title": "December to March",
                      "description": "Short explanation why this period is ideal."
                    },
                    {
                      "title": "Summer",
                      "description": "Short explanation for this season."
                    }
                  ]
                }
              ]
            }
            
            Content rules:
            
            - For each country, provide between 2 and 5 best times to visit.
            - Each "best_times" entry MUST have:
              - "title": a concise time period, for example:
                - "December to March"
                - "First week of December"
                - "Summer"
                - "Late April to Early June"
                - "During Cherry Blossom Season"
              - "description": 1–2 short sentences explaining why this period is ideal
                (weather, seasons, festivals, natural phenomena, prices, tourist crowds, etc.).
            - Use realistic climate, seasons, events, and natural conditions for each country.
            - Do NOT invent unknown or extremely obscure festivals; prefer widely known or generic events.
            - Absolutely no extra top-level keys and no extra text outside the JSON object.
        """).strip()

    def build_user_prompt(self, countries: List[Country]) -> str:
        """Build the user prompt for best times assignment task.

        Args:
            countries: List of countries to get best times for.

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
            
            For each country in the list above, generate 2–5 of the best times to visit.
            
            Formatting rules:
            
            - Your ENTIRE response must be a single JSON object.
            - That JSON object must have exactly one top-level property named "assignments".
            - The value of "assignments" must be an array.
            - Each element of this array must describe one country and must contain:
              - "country_iso2": the ISO2 country code as provided in the list.
              - "best_times": an array of 2–5 objects.
            - Each object inside "best_times" must contain:
              - "title": a concise time period (for example: "December to March", "First week of December", "Summer", "Late April to Early June", "During Cherry Blossom Season").
              - "description": 1–2 sentences explaining why this period is a good time to visit (weather, seasons, festivals, natural phenomena, prices, tourist crowds, etc.).
            
            Do not include any keys other than "assignments" at the top level.
            Do not include any text outside of the JSON object.
            Return the JSON object for the given countries only.
        """).strip()

    def parse_response(self, content: str) -> List[CountryBestTimeAssignment]:
        """Parse the LLM response and return list of assignments.

        Args:
            content: Raw JSON content from LLM.

        Returns:
            List of CountryBestTimeAssignment objects.

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

        # Convert to CountryBestTimeAssignment objects
        result = []
        for assignment in assignments:
            if not isinstance(assignment, dict):
                raise RuntimeError(
                    f"Invalid assignment format: {assignment} (expected dict)"
                )
            country_iso2 = assignment.get("country_iso2")
            best_times = assignment.get("best_times", [])

            if not country_iso2:
                raise RuntimeError(
                    f"Assignment missing country_iso2: {assignment}"
                )
            if not isinstance(best_times, list):
                raise RuntimeError(
                    f"Assignment best_times must be a list: {assignment}"
                )

            # Validate each best_time has title and description
            validated_best_times = []
            for best_time in best_times:
                if not isinstance(best_time, dict):
                    raise RuntimeError(
                        f"Invalid best_time format: {best_time} (expected dict)"
                    )
                title = best_time.get("title")
                description = best_time.get("description")
                if not title or not description:
                    raise RuntimeError(
                        f"Best time missing title or description: {best_time}"
                    )
                validated_best_times.append({
                    "title": str(title),
                    "description": str(description),
                })

            result.append(
                CountryBestTimeAssignment(
                    country_iso2=str(country_iso2).upper(),
                    best_times=validated_best_times,
                )
            )

        return result

    def get_best_times_for_countries(
        self, countries: List[Country]
    ) -> List[CountryBestTimeAssignment]:
        """Get best times for countries using OpenAI.

        Args:
            countries: List of countries to get best times for.

        Returns:
            List of CountryBestTimeAssignment objects.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If LLM returns invalid JSON or unexpected structure.
        """
        if not countries:
            raise ValueError("Countries list cannot be empty")

        return self.execute(countries=countries)

