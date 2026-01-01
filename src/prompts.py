"""
Story generation prompts for different age groups and languages.
"""

# Language names for prompts (in the target language)
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "it": "Italian (Italiano)",
    "pt": "Portuguese (Português)",
    "nl": "Dutch (Nederlands)",
    "pl": "Polish (Polski)",
    "ru": "Russian (Русский)",
    "ja": "Japanese (日本語)",
    "zh": "Chinese (中文)",
    "ko": "Korean (한국어)",
    "ar": "Arabic (العربية)",
    "hi": "Hindi (हिन्दी)",
    "tr": "Turkish (Türkçe)",
    "sv": "Swedish (Svenska)",
    "da": "Danish (Dansk)",
    "no": "Norwegian (Norsk)",
    "fi": "Finnish (Suomi)",
    "cs": "Czech (Čeština)",
    "el": "Greek (Ελληνικά)",
    "he": "Hebrew (עברית)",
    "hu": "Hungarian (Magyar)",
    "ro": "Romanian (Română)",
    "uk": "Ukrainian (Українська)",
}

AGE_GROUPS = {
    "toddler": {
        "label": "Toddler (2-3)",
        "duration": "5-8 minutes",
        "word_count": 500,
        "complexity": "very simple sentences, lots of repetition, familiar objects and animals, gentle and reassuring tone"
    },
    "preschool": {
        "label": "Preschool (3-5)",
        "duration": "8-12 minutes",
        "word_count": 800,
        "complexity": "short paragraphs, basic adventure with happy resolution, simple dialogue, colorful descriptions"
    },
    "early_reader": {
        "label": "Early Reader (5-7)",
        "duration": "12-15 minutes",
        "word_count": 1000,
        "complexity": "light dialogue between characters, simple problem-solving, positive messages, mild excitement with calm ending"
    },
    "older_kids": {
        "label": "Older Kids (7+)",
        "duration": "15-20 minutes",
        "word_count": 1300,
        "complexity": "fuller narrative arc, character development, gentle life lessons, engaging plot with satisfying resolution"
    }
}

THEMES = [
    "Pirates & Treasure",
    "Space Adventure",
    "Dinosaur Discovery",
    "Princess & Castle",
    "Animals & Safari",
    "Underwater World",
    "Superheroes",
    "Magic & Wizards",
    "Robots & Inventions",
]


def get_story_prompt(child_name: str, age_group: str, theme: str, language: str = "en") -> str:
    """Generate the prompt for story creation.

    Args:
        child_name: The child's name to feature in the story.
        age_group: One of 'toddler', 'preschool', 'early_reader', 'older_kids'.
        theme: The story theme.
        language: Language code for the story (e.g., 'en', 'es', 'fr').

    Returns:
        The formatted prompt for story generation.
    """
    age_config = AGE_GROUPS.get(age_group, AGE_GROUPS["preschool"])
    language_name = LANGUAGE_NAMES.get(language, "English")

    # Language instruction
    language_instruction = ""
    if language != "en":
        language_instruction = f"""
LANGUAGE REQUIREMENT:
- Write the ENTIRE story in {language_name}
- Use natural, fluent {language_name} appropriate for children
- Keep cultural references appropriate for {language_name}-speaking audiences
"""

    prompt = f"""You are a warm, caring children's storyteller. Write a bedtime story for a {age_config['label'].lower()} child.

STORY REQUIREMENTS:
- Main character name: {child_name}
- Theme: {theme}
- Target length: approximately {age_config['word_count']} words ({age_config['duration']} when read aloud)
- Writing style: {age_config['complexity']}{language_instruction}

STORY STRUCTURE:
1. GENTLE OPENING: Introduce {child_name} in a cozy, familiar setting
2. DISCOVERY: {child_name} discovers something exciting related to {theme}
3. SMALL ADVENTURE: A fun, age-appropriate adventure unfolds (no real danger)
4. POSITIVE RESOLUTION: Everything works out wonderfully
5. CALM ENDING: {child_name} returns home feeling happy and sleepy, ready for dreams

IMPORTANT RULES:
- Use {child_name}'s name naturally throughout (at least 8-10 times)
- NO scary content, villains, monsters, or danger
- NO violence, conflict, or sad moments
- NO complex vocabulary - keep it age-appropriate
- NO cliffhangers - the story must have a complete, satisfying ending
- The ending should be calming and sleep-inducing
- Use warm, reassuring language throughout

Write the complete story now. Do not include a title - just start with the story text."""

    return prompt


def get_system_prompt() -> str:
    """Get the system prompt for the story generator."""
    return """You are a professional children's story writer specializing in bedtime stories.
Your stories are:
- Warm, gentle, and reassuring
- Age-appropriate and engaging
- Perfect for helping children fall asleep
- Full of wonder and positive messages

You always follow the exact requirements given and never include scary or inappropriate content.
You write stories that parents trust and children love."""
