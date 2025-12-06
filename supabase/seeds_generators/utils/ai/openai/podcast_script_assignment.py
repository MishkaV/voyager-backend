"""OpenAI task for generating podcast scripts for countries."""

import dataclasses
import textwrap
from typing import List

from utils.database.country_repository import Country
from utils.ai.openai.base_openai_client import BaseOpenAIClient
from utils.settings.voyager_settings import VoyagerSeedSettings


@dataclasses.dataclass
class PodcastScriptAssignment:
    """Model for LLM response with podcast script for a country."""

    country_iso2: str
    script: str


class PodcastScriptAssignmentClient(BaseOpenAIClient):
    """Client for generating podcast scripts for countries using OpenAI."""

    # Batch size for processing countries (scripts are long, process one at a time)
    BATCH_SIZE: int = 1

    @property
    def system_prompt(self) -> str:
        """Return the system prompt for podcast script generation task."""
        return textwrap.dedent("""
            You are an expert travel storyteller and podcast scriptwriter.
            Your task is to generate a polished, engaging, medium-length podcast script about a specific country.
            
            GENERAL REQUIREMENTS:
            - The podcast must feature exactly two speakers:
              - Alex
              - Maya
            - Alex and Maya are co-hosts and equal conversational partners.
            - The tone should be warm, engaging, conversational, and easy to listen to.
            - The script should feel like a real podcast episode, not an article being read aloud.
            - Both speakers can ask questions, react, share insights, and tell short anecdotes.
            - All statements must be realistic and based on widely known or easily verifiable information.
            - You MUST avoid invented historical claims, made-up festivals, or overly specific data that cannot be confirmed.
            - You MAY include cultural insights, geography, travel highlights, regional differences, famous foods, and practical travel expectations.
            - You may structure the dialogue as a mix of questions and answers, commentary, and natural transitions.
            
            LENGTH / TOKENS (IMPORTANT):
            - Keep the script MEDIUM in length, roughly suitable for about 6–9 minutes of spoken audio.
            - As a guideline, aim for around 900–1400 words in total (approximately 1,300–1,800 tokens).
            - Prefer concise, dense, vivid content over long-winded explanations.
            - Do NOT produce an overly long script; if in doubt, be slightly shorter rather than longer.
            
            VOYAGER SIGNATURE INTRO (CRITICAL):
            - Always begin the podcast with a Voyager-branded greeting from Alex.
            - The VERY FIRST dialogue line after the initial style instruction MUST be spoken by Alex and MUST include:
              - a friendly greeting,
              - a clear mention of "Voyager",
              - a clear mention that this episode is about the given country.
            - For example (you MUST adapt it, not copy verbatim):
              "Alex: Hey travelers, welcome to Voyager — your companion for exploring the world. Today we're heading to <COUNTRY_NAME>…"
            - You may lightly adapt the wording and vibe of this greeting to match the atmosphere of the specific country, but:
              - It must clearly welcome listeners.
              - It must clearly mention "Voyager".
              - It must clearly set up that the episode is about the given country.
            
            CLOSING SEGMENT WITH REFLECTION QUESTIONS (CRITICAL):
            - At the end of the episode, there MUST be a short signature closing segment for listeners.
            - This segment should:
              1) Explicitly say that, as a Voyager tradition, the hosts leave listeners with a question or questions to think about.
                 For example (adapt the wording to the country and episode tone):
                 "Maya: And as we always do here on Voyager, we'd love to leave you with a couple of questions to think about…"
              2) Include 1–2 short, thought-provoking questions addressed directly to the listeners about the country
                 (they can be asked by Alex, Maya, or both). These questions should invite reflection or inspiration, not require a factual answer.
              3) End with a brief, warm farewell line that:
                 - is spoken by Alex,
                 - thanks listeners,
                 - mentions "Voyager" again,
                 - and closes the episode in a friendly way.
                 For example (you MUST adapt it, not copy literally):
                 "Alex: Thanks for traveling with us on Voyager today. Until our next journey together, take care and keep exploring."
            
            - The final line of the entire script MUST be Alex's farewell line as described above.
            - Do NOT add anything after Alex's farewell.
            
            OUTPUT FORMAT (CRITICAL):
            Return ONLY the podcast script in the following structure:
            
            Please read aloud the following in a podcast interview style:
            Alex: <first line of dialogue (Voyager greeting)>
            Maya: <response>
            Alex: <next turn>
            Maya: <next turn>
            ...continue alternating and varying naturally...
            Maya or Alex: <intro to the reflection questions segment for listeners>
            Alex or Maya: <1st question for listeners>
            (optional) Alex or Maya: <2nd question for listeners>
            Alex: <final Voyager-themed farewell line>
            
            RULES FOR THE FORMAT:
            - No headings, no markdown, no bullets — only dialogue lines.
            - Speaker names MUST be exactly:
              - "Alex"
              - "Maya"
            - The very first line MUST begin with:
              "Please read aloud the following in a podcast interview style:"
            - The first speaker after that line MUST be Alex (with the Voyager greeting).
            - No narration outside dialogue.
            - No stage directions (like [laughter] or [music]).
            - No meta-comments about being an AI.
            - The last line MUST be Alex's farewell line to the listeners, including a mention of "Voyager".
            
            The user prompt will supply:
            - the country name,
            - a link to a real Wikipedia page,
            - additional metadata when available.
            
            Use that data to craft an accurate, engaging podcast episode that:
            - opens with a Voyager-branded greeting from Alex,
            - explores the country in a lively conversation between Alex and Maya,
            - and ends with a short Voyager "questions to reflect on" segment plus a warm farewell from Alex.
        """).strip()

    def build_user_prompt(self, country: Country, wikipedia_url: str) -> str:
        """Build the user prompt for podcast script generation task.

        Args:
            country: Country to generate script for.
            wikipedia_url: Wikipedia URL for the country.

        Returns:
            User prompt string with placeholders replaced.
        """
        return textwrap.dedent(f"""
            Generate a podcast script about the following country:
            
            Country: {country.name}
            Wikipedia URL: {wikipedia_url}
            
            The episode should:
            - introduce the country in an engaging way,
            - highlight cultural identity, landscapes, travel experiences, food, regional variety,
            - give travelers a sense of what is special or unique about the destination,
            - provide friendly and realistic insights,
            - avoid niche, unverifiable facts.
            
            Follow all formatting and structural rules from the system prompt.
            Return ONLY the script.
        """).strip()

    def parse_response(self, content: str) -> str:
        """Parse the LLM response and return script as string.

        Args:
            content: Raw text content from LLM (the podcast script).

        Returns:
            Script string.
        """
        if not content or not content.strip():
            raise RuntimeError("LLM returned empty script")
        return content.strip()

    def execute(self, country: Country, wikipedia_url: str) -> str:
        """Execute the task with given parameters.

        Overrides base execute() to return plain text instead of JSON.

        Args:
            country: Country to generate script for.
            wikipedia_url: Wikipedia URL for the country.

        Returns:
            Podcast script as string.

        Raises:
            RuntimeError: If task execution fails.
        """
        system_prompt = self.system_prompt
        user_prompt = self.build_user_prompt(country=country, wikipedia_url=wikipedia_url)

        # Call API without JSON format (plain text response)
        content = self._call_api(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=None,  # Plain text, not JSON
        )

        return self.parse_response(content)

    def get_script_for_country(
        self, country: Country, wikipedia_url: str
    ) -> PodcastScriptAssignment:
        """Get podcast script for a country using OpenAI.

        Args:
            country: Country to generate script for.
            wikipedia_url: Wikipedia URL for the country.

        Returns:
            PodcastScriptAssignment object with country_iso2 and script.

        Raises:
            ValueError: If inputs are invalid.
            RuntimeError: If LLM returns invalid response.
        """
        if not country:
            raise ValueError("Country cannot be None")
        if not wikipedia_url:
            raise ValueError("Wikipedia URL cannot be empty")

        script = self.execute(country=country, wikipedia_url=wikipedia_url)

        return PodcastScriptAssignment(
            country_iso2=country.iso2.upper(),
            script=script,
        )

