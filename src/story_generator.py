"""
Story generation using Groq API with Llama 3.3.
"""

import os
from groq import Groq
from .prompts import get_story_prompt, get_system_prompt


class StoryGenerator:
    """Generate personalized children's stories using Groq LLM."""

    def __init__(self, api_key: str = None):
        """Initialize the story generator.

        Args:
            api_key: Groq API key. If not provided, reads from GROQ_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter."
            )
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate_story(
        self,
        child_name: str,
        age_group: str,
        theme: str,
        language: str = "en",
        max_retries: int = 2
    ) -> str:
        """Generate a personalized story.

        Args:
            child_name: The child's name to feature in the story.
            age_group: One of 'toddler', 'preschool', 'early_reader', 'older_kids'.
            theme: The story theme (e.g., 'Pirates & Treasure').
            language: Language code for the story (e.g., 'en', 'es', 'fr').
            max_retries: Number of retries on failure.

        Returns:
            The generated story text.

        Raises:
            Exception: If story generation fails after retries.
        """
        # Clean and validate input
        child_name = child_name.strip().title()
        if not child_name:
            raise ValueError("Child's name cannot be empty")

        # Get prompts
        system_prompt = get_system_prompt()
        user_prompt = get_story_prompt(child_name, age_group, theme, language)

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=4000,
                    top_p=0.9,
                )

                story = response.choices[0].message.content.strip()

                # Basic validation
                if len(story) < 200:
                    raise ValueError("Generated story is too short")

                # Check if child's name appears in the story
                if child_name.lower() not in story.lower():
                    raise ValueError("Story doesn't include child's name")

                return story

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    continue
                raise Exception(
                    f"Failed to generate story after {max_retries + 1} attempts: {str(last_error)}"
                )

    def estimate_duration(self, text: str, words_per_minute: int = 130) -> float:
        """Estimate audio duration in minutes.

        Args:
            text: The story text.
            words_per_minute: Speaking rate (default 130 for children's stories).

        Returns:
            Estimated duration in minutes.
        """
        word_count = len(text.split())
        return word_count / words_per_minute
