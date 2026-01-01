"""
Story generation prompts for different age groups.
"""

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


def get_story_prompt(child_name: str, age_group: str, theme: str) -> str:
    """Generate the prompt for story creation."""

    age_config = AGE_GROUPS.get(age_group, AGE_GROUPS["preschool"])

    prompt = f"""You are a warm, caring children's storyteller. Write a bedtime story for a {age_config['label'].lower()} child.

STORY REQUIREMENTS:
- Main character name: {child_name}
- Theme: {theme}
- Target length: approximately {age_config['word_count']} words ({age_config['duration']} when read aloud)
- Writing style: {age_config['complexity']}

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
