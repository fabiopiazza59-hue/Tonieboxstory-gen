# -*- coding: utf-8 -*-
"""
Personalized Story Generator - Main Application
A free SaaS for generating personalized audio stories for Toniebox Creative-Tonies.
"""

import gradio as gr
import os
import time

from src.story_generator import StoryGenerator
from src.tts_engine import TTSEngine, VOICES, LANGUAGES, get_voices_for_language, get_default_voice_for_language
from src.rate_limiter import MAX_STORIES_PER_DAY
from src.prompts import AGE_GROUPS, THEMES


# Check if we're in demo mode (no API key)
DEMO_MODE = not os.environ.get("GROQ_API_KEY")

# Initialize components (lazy loading)
story_generator = None
tts_engine = None


def get_story_generator():
    """Lazy initialization of story generator."""
    global story_generator
    if story_generator is None:
        story_generator = StoryGenerator()
    return story_generator


def get_tts_engine():
    """Lazy initialization of TTS engine."""
    global tts_engine
    if tts_engine is None:
        tts_engine = TTSEngine()
    return tts_engine


def generate_demo_story(child_name: str, theme: str) -> str:
    """Generate a demo story for UI testing when no API key is set."""
    return f"""Once upon a time, in a land filled with wonder and magic, there lived a brave young adventurer named {child_name}.
{child_name} had always dreamed of going on a {theme.lower()} adventure. One sunny morning, {child_name} woke up to find a mysterious golden envelope on their pillow.
"Dear {child_name}," the letter read, "You have been chosen for a special quest!"
With excitement bubbling in their heart, {child_name} packed a small bag with snacks and their favorite toy. The adventure was about to begin!
Along the way, {child_name} met friendly creatures who helped guide the path. There was a wise owl who shared secrets of the forest, and a playful bunny who knew all the shortcuts.
"You're very brave, {child_name}!" said the owl. "Keep going, you're almost there!"
Finally, after climbing over mossy logs and crossing a sparkling stream, {child_name} reached the treasure - a beautiful chest filled with the most precious thing of all: memories of this wonderful adventure.
As the stars began to twinkle in the evening sky, {child_name} headed home, heart full of joy. Snuggling into bed, {child_name} closed their eyes and dreamed of tomorrow's adventures.
The End.
Sweet dreams, {child_name}."""


def generate_story_and_audio(
    child_name: str,
    age_group: str,
    language: str,
    theme: str,
    custom_theme: str,
    voice: str
):
    """Generate a personalized story and convert to audio."""

    # Validate inputs
    if not child_name or not child_name.strip():
        return "", None, "Please enter your child's name."

    # Clean name (letters, spaces, hyphens only, plus unicode for international names)
    clean_name = "".join(c for c in child_name if c.isalpha() or c in " -'")
    if not clean_name:
        return "", None, "Please enter a valid name (letters only)."

    # Determine theme
    final_theme = custom_theme.strip() if theme == "Custom" else theme
    if not final_theme:
        return "", None, "Please select a theme or enter a custom theme."

    try:
        # Step 1: Generate story
        if DEMO_MODE:
            # Demo mode - use sample story
            time.sleep(1)  # Simulate generation time
            story_text = generate_demo_story(clean_name, final_theme)
        else:
            generator = get_story_generator()
            story_text = generator.generate_story(
                child_name=clean_name,
                age_group=age_group,
                theme=final_theme,
                language=language
            )

        # Step 2: Generate audio
        audio_path = None
        try:
            tts = get_tts_engine()
            audio_path = tts.generate_audio(
                text=story_text,
                voice=voice,
                output_format="mp3"
            )
        except Exception as tts_error:
            # If TTS fails, still return the story without audio
            print(f"TTS Error: {tts_error}")

        # Calculate estimated duration
        word_count = len(story_text.split())
        duration_min = word_count / 130  # ~130 words per minute
        duration_str = f"{int(duration_min)} min {int((duration_min % 1) * 60)} sec"

        demo_note = "\n\n*Demo mode - set GROQ_API_KEY for AI-generated stories*" if DEMO_MODE else ""
        audio_note = "\n\n*Audio generation requires edge-tts*" if audio_path is None else ""

        status_msg = (
            f"Story created for {clean_name}!\n\n"
            f"Duration: ~{duration_str}{demo_note}{audio_note}"
        )

        return story_text, audio_path, status_msg

    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "GROQ_API_KEY" in error_msg:
            error_msg = "Service temporarily unavailable. Please try again later."
        return "", None, f"Oops! {error_msg}"


def update_custom_theme_visibility(theme: str):
    """Show/hide custom theme input based on theme selection."""
    return gr.update(visible=(theme == "Custom"))


def get_all_voice_choices():
    """Get all voices grouped by language for the dropdown."""
    choices = []
    for lang_code, lang_info in LANGUAGES.items():
        voices = get_voices_for_language(lang_code)
        for voice_key, voice_info in voices.items():
            choices.append((voice_info["label"], voice_key))
    return choices


# Build the Gradio interface
with gr.Blocks(
    title="Personalized Story Generator",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="pink",
    ),
) as app:

    # Header
    gr.Markdown(
        """
        # Personalized Story Generator
        Create magical bedtime stories for your child's **Toniebox Creative-Tonie**!
        Simply enter your child's name, pick a theme, and we'll generate a unique story
        with audio ready to upload to your Creative-Tonie.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Story Details")

            child_name = gr.Textbox(
                label="Child's Name",
                placeholder="Enter your child's name...",
                max_lines=1,
            )

            age_group = gr.Radio(
                choices=[(v["label"], k) for k, v in AGE_GROUPS.items()],
                label="Age Group",
                value="preschool",
            )

            theme = gr.Dropdown(
                choices=THEMES + ["Custom"],
                label="Theme",
                value="Pirates & Treasure",
            )

            custom_theme = gr.Textbox(
                label="Custom Theme",
                placeholder="Describe your custom theme...",
                visible=False,
                max_lines=2,
            )

            language = gr.Dropdown(
                choices=[(v["label"], k) for k, v in LANGUAGES.items()],
                label="Story Language",
                value="en",
            )

            # All voices - user selects voice matching their language choice
            voice = gr.Dropdown(
                choices=get_all_voice_choices(),
                label="Voice (select voice matching your language)",
                value="en_warm_female_us",
            )

            generate_btn = gr.Button(
                "Generate Story",
                variant="primary",
                size="lg",
            )

        with gr.Column(scale=1):
            gr.Markdown("### Your Story")

            status_output = gr.Markdown(
                value="Enter details and click 'Generate Story' to begin!"
            )

            story_output = gr.Textbox(
                label="Story Preview",
                lines=10,
                max_lines=15,
                interactive=False,
            )

            audio_output = gr.Audio(
                label="Listen to Your Story",
                type="filepath",
            )

    gr.Markdown(
        """
        ---
        ### How to Use Your Story
        1. **Download** the MP3 file using the download button on the audio player
        2. **Open** [my.tonies.com](https://my.tonies.com) or the **mytonies app**
        3. **Upload** the MP3 to your Creative-Tonie
        4. **Place** the Creative-Tonie on your Toniebox to sync
        5. **Enjoy** your personalized story!
        ---
        *Made with love for little dreamers everywhere*
        """
    )

    # Event handlers
    theme.change(
        fn=update_custom_theme_visibility,
        inputs=[theme],
        outputs=[custom_theme],
    )

    generate_btn.click(
        fn=generate_story_and_audio,
        inputs=[child_name, age_group, language, theme, custom_theme, voice],
        outputs=[story_output, audio_output, status_output],
    )


if __name__ == "__main__":
    app.launch()
