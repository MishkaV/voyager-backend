"""OpenAI task for assigning AI suggestions to countries."""

import dataclasses
import textwrap
from abc import abstractmethod
from typing import List, Optional

from utils.database.country_repository import Country
from utils.ai.openai.base_openai_client import BaseOpenAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class CountryAISuggestAssignment:
    """Model for LLM response assigning AI suggestions."""

    suggest_text: str
    prompt: str
    country_iso2: Optional[str] = None


class BaseCountryAISuggestAssignmentClient(BaseOpenAIClient):
    """Base client for assigning AI suggestions using OpenAI."""

    # Batch size for processing countries
    BATCH_SIZE: int = 20

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for AI suggestions assignment task."""
        return textwrap.dedent("""
            You are helping to design a library of AI suggestion templates for a travel planning app.
            
            Each suggestion stored in the database has:
            - "suggest_text": a short UI-facing label (1 line, max 80 characters, no emojis).
            - "prompt": a reusable English instruction template that will be sent to the AI model at runtime.
            - Optionally, a "country_iso2" field if the suggestion is country-specific.
            
            There are two modes of operation:
            
            1) GENERAL mode
               - Suggestions are NOT tied to any specific country.
               - Output objects MUST NOT include "country_iso2".
               - Prompts must be generic and reusable for many destinations.
               - Prompts may use placeholders in double curly braces, e.g.:
                 {{COUNTRY_NAME}}, {{DESTINATION_NAME}}, {{TRIP_LENGTH_DAYS}}, {{BUDGET_LEVEL}}, {{TRAVELER_TYPE}}, {{USER_GOAL}}.
            
            2) COUNTRY_SPECIFIC mode
               - Suggestions are tied to specific countries.
               - Output objects MUST include "country_iso2" for each suggestion.
               - Prompts must clearly reflect that they are about that country (typical regions, trip styles, experiences, seasons).
               - Prompts may use placeholders such as:
                 {{COUNTRY_NAME}}, {{REGION}}, {{CITY_NAME}}, {{TRIP_LENGTH_DAYS}}, {{BUDGET_LEVEL}}, {{SEASON}}, {{TRAVELER_TYPE}}.
            
            The user prompt will tell you which mode to use and may provide a list of countries.
            
            OUTPUT FORMAT (CRITICAL):
            
            - You MUST return a single JSON OBJECT at the top level.
            - This JSON object MUST contain exactly one key: "assignments".
            - "assignments" MUST be an array.
            - Each element inside "assignments" MUST contain:
                - "suggest_text": short, UI-facing label.
                - "prompt": reusable instruction template in English.
                - OPTIONAL: "country_iso2" (only in COUNTRY_SPECIFIC mode; forbidden in GENERAL mode).
            
            Rules for "suggest_text":
            - Max length: 50 characters.
            - No emojis.
            - Either an action-style label (e.g. "Plan a remote-work friendly trip")
              or a natural question a traveler might click (e.g. "How do I get from the airport to the city center?").
            - Within one generation call, all "suggest_text" values must be clearly different in meaning.
            
            Rules for "prompt":
            - Written as instructions to the AI model (e.g. "You are a travel planner who helps the user...").
            - Clearly describe what the model should do and how detailed the answer should be.
            - When helpful, describe the structure of the answer (sections, bullet points, day-by-day outline, etc.).
            - Use placeholders {{LIKE_THIS}} for dynamic values, rather than hard-coding unknown details.
            - In GENERAL mode, prompts must not assume a specific country or city.
            - In COUNTRY_SPECIFIC mode, prompts should reference realistic travel patterns and experiences for that country at a high level.
            
            Diversity guidelines (apply in all modes unless overridden in the user prompt):
            - Cover a wide range of traveler needs: itinerary planning, first things to see, airport–city transfers,
              where to stay, budget vs comfort, food/nightlife/nature/culture themes, safety, etiquette, packing, short vs long trips, etc.
            - A meaningful portion of suggestions should be phrased as questions (ending with "?"),
              and the rest as action-style labels.
            
            EXAMPLE STRUCTURE (for illustration only):
            
            {
              "assignments": [
                {
                  "suggest_text": "Plan a remote-work friendly trip",
                  "prompt": "You are a travel planner who helps the user design a remote-work friendly trip to {{COUNTRY_NAME}} or another destination. Ask about their work schedule, internet needs, budget, and preferred vibe, then propose 2–3 location options with pros and cons and a rough structure for the stay."
                },
                {
                  "country_iso2": "JP",
                  "suggest_text": "First-time trip to Japan: what should I see?",
                  "prompt": "You are a travel planner helping a user plan their first trip to {{COUNTRY_NAME}}. Given their trip length and interests, outline the key regions or cities they should visit, explain why, and suggest a high-level day-by-day structure. Focus on realistic routes and typical first-time highlights."
                }
              ]
            }
            
            Do not include any text outside the JSON object in your final answer.
        """).strip()

    @abstractmethod
    def build_user_prompt(self, **kwargs) -> str:
        """Build the user prompt for AI suggestions assignment task.

        Args:
            **kwargs: Task-specific parameters.

        Returns:
            User prompt string.
        """
        pass

    def parse_response(self, content: str) -> List[CountryAISuggestAssignment]:
        """Parse the LLM response and return list of assignments.

        Args:
            content: Raw JSON content from LLM.

        Returns:
            List of CountryAISuggestAssignment objects.

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

        # Convert to CountryAISuggestAssignment objects
        result = []
        for assignment in assignments:
            if not isinstance(assignment, dict):
                raise RuntimeError(
                    f"Invalid assignment format: {assignment} (expected dict)"
                )
            suggest_text = assignment.get("suggest_text")
            prompt = assignment.get("prompt")
            country_iso2 = assignment.get("country_iso2")

            if not suggest_text:
                raise RuntimeError(
                    f"Assignment missing suggest_text: {assignment}"
                )
            if not prompt:
                raise RuntimeError(
                    f"Assignment missing prompt: {assignment}"
                )

            # Process country_iso2: convert to uppercase string if present, otherwise None
            processed_country_iso2 = None
            if country_iso2:
                processed_country_iso2 = str(country_iso2).upper()

            result.append(
                CountryAISuggestAssignment(
                    suggest_text=str(suggest_text),
                    prompt=str(prompt),
                    country_iso2=processed_country_iso2,
                )
            )

        return result


class GeneralAISuggestAssignmentClient(BaseCountryAISuggestAssignmentClient):
    """Client for generating general AI suggestions (not country-specific)."""

    def build_user_prompt(self, **kwargs) -> str:
        """Build the user prompt for general AI suggestions.

        Returns:
            User prompt string.
        """
        return textwrap.dedent("""
            MODE: GENERAL

            Generate 10–15 GENERAL travel-planner suggestion templates.
            
            Constraints:
            - Do NOT include the field "country_iso2" in any object.
            - Suggestions must be reusable for many destinations and not tied to a specific country or city.
            - At least one third of the suggestions MUST be phrased as natural questions ending with a question mark.
            - The rest can be action-style labels.
            - Cover a broad range of traveler needs (itinerary planning, first things to see, airport transfers, where to stay, budgeting, themes like food/nature/nightlife, safety, etiquette, packing, short vs long trips, different traveler types).
            
            Remember:
            - Follow the output format specified in the system message (JSON object with the key "assignments").
            - Return ONLY the JSON object and nothing else.
        """).strip()

    def get_suggests(self) -> List[CountryAISuggestAssignment]:
        """Get general AI suggestions using OpenAI.

        Returns:
            List of CountryAISuggestAssignment objects (without country_iso2).

        Raises:
            RuntimeError: If LLM returns invalid JSON or unexpected structure.
        """
        return self.execute()


class CountrySpecificAISuggestAssignmentClient(BaseCountryAISuggestAssignmentClient):
    """Client for generating country-specific AI suggestions."""

    def build_user_prompt(self, countries: List[Country], **kwargs) -> str:
        """Build the user prompt for country-specific AI suggestions.

        Args:
            countries: List of countries to get suggestions for.

        Returns:
            User prompt string.
        """
        # Format countries list as shown in country_best_time_assignment.py
        countries_list = "\n".join(
            f"- {c.iso2}: {c.name}, capital {c.capital}, continent {c.continent}"
            for c in countries
        )

        return textwrap.dedent(f"""
            MODE: COUNTRY_SPECIFIC

            Here is the list of countries:
            
            {countries_list}
            
            For EACH country in this list, generate 3–6 COUNTRY-SPECIFIC travel-planner suggestion templates.
            
            Constraints:
            - Every suggestion object MUST include "country_iso2" matching one of the countries in the list.
            - Suggestions must clearly reflect typical ways people travel in that country
              (for example: common regions, mix of cities and nature, beach vs inland, road trips, cultural highlights, etc.).
            - At least one third of the suggestions for each country MUST be phrased as natural questions ending with a question mark.
            - The rest can be action-style labels.
            - Vary traveler intentions: first-time visits, choosing regions, short vs long trips, food-focused trips, nature trips, family trips, solo and remote-work trips, safety/etiquette, getting around inside the country, etc.
            
            Remember:
            - Follow the output format specified in the system message (JSON object with the key "assignments").
            - Return ONLY the JSON object and nothing else.
        """).strip()

    def get_suggests_for_countries(
        self, countries: List[Country]
    ) -> List[CountryAISuggestAssignment]:
        """Get country-specific AI suggestions for countries using OpenAI.

        Args:
            countries: List of countries to get suggestions for.

        Returns:
            List of CountryAISuggestAssignment objects (with country_iso2).

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If LLM returns invalid JSON or unexpected structure.
        """
        if not countries:
            raise ValueError("Countries list cannot be empty")

        return self.execute(countries=countries)

