# -*- coding: utf-8 -*-
"""
Personalized Story Generator - Main Application

A free SaaS for generating personalized audio stories for Toniebox Creative-Tonies.
"""

import gradio as gr
import os
import time

from src.story_generator import StoryGenerator
from src.tts_engine import TTSEngine, VOICES, LANGUAGES
from src.rate_limiter import MAX_STORIES_PER_DAY
from src.prompts import AGE_GROUPS, THEMES


# Check if we're in demo mode (no API key)
DEMO_MODE = not os.environ.get("GROQ_API_KEY")

# Initialize components (lazy loading)
story_generator = None
tts_engine = None

# Pre-compute dropdown choices as simple lists (Gradio 4.44 compatibility)
LANGUAGE_CHOICES = [
    ("English", "en"),
    ("Español (Spanish)", "es"),
    ("Français (French)", "fr"),
    ("Deutsch (German)", "de"),
    ("Italiano (Italian)", "it"),
    ("Português (Portuguese)", "pt"),
    ("Nederlands (Dutch)", "nl"),
    ("Polski (Polish)", "pl"),
    ("Русский (Russian)", "ru"),
    ("日本語 (Japanese)", "ja"),
    ("中文 (Chinese)", "zh"),
    ("한국어 (Korean)", "ko"),
    ("العربية (Arabic)", "ar"),
    ("हिन्दी (Hindi)", "hi"),
    ("Türkçe (Turkish)", "tr"),
    ("Svenska (Swedish)", "sv"),
    ("Dansk (Danish)", "da"),
    ("Norsk (Norwegian)", "no"),
    ("Suomi (Finnish)", "fi"),
    ("Čeština (Czech)", "cs"),
    ("Ελληνικά (Greek)", "el"),
    ("עברית (Hebrew)", "he"),
    ("Magyar (Hungarian)", "hu"),
    ("Română (Romanian)", "ro"),
    ("Українська (Ukrainian)", "uk"),
]

VOICE_CHOICES = [
    ("Warm Female (US)", "en_warm_female_us"),
    ("Friendly Male (US)", "en_friendly_male_us"),
    ("Friendly Male (UK)", "en_friendly_male_uk"),
    ("Storyteller (AU)", "en_storyteller_au"),
    ("Elvira (Spain)", "es_warm_female"),
    ("Alvaro (Spain)", "es_friendly_male"),
    ("Dalia (Mexico)", "es_mx_female"),
    ("Jorge (Mexico)", "es_mx_male"),
    ("Denise (France)", "fr_warm_female"),
    ("Henri (France)", "fr_friendly_male"),
    ("Sylvie (Canada)", "fr_ca_female"),
    ("Katja (Germany)", "de_warm_female"),
    ("Conrad (Germany)", "de_friendly_male"),
    ("Ingrid (Austria)", "de_at_female"),
    ("Elsa (Italy)", "it_warm_female"),
    ("Diego (Italy)", "it_friendly_male"),
    ("Francisca (Brazil)", "pt_br_female"),
    ("Antonio (Brazil)", "pt_br_male"),
    ("Raquel (Portugal)", "pt_pt_female"),
    ("Colette (Netherlands)", "nl_warm_female"),
    ("Maarten (Netherlands)", "nl_friendly_male"),
    ("Agnieszka (Poland)", "pl_warm_female"),
    ("Marek (Poland)", "pl_friendly_male"),
    ("Svetlana (Russia)", "ru_warm_female"),
    ("Dmitry (Russia)", "ru_friendly_male"),
    ("Nanami (Japan)", "ja_warm_female"),
    ("Keita (Japan)", "ja_friendly_male"),
    ("Xiaoxiao (China)", "zh_warm_female"),
    ("Yunxi (China)", "zh_friendly_male"),
    ("Hsiao (Taiwan)", "zh_tw_female"),
    ("SunHi (Korea)", "ko_warm_female"),
    ("InJoon (Korea)", "ko_friendly_male"),
    ("Zariyah (Saudi)", "ar_warm_female"),
    ("Hamed (Saudi)", "ar_friendly_male"),
    ("Salma (Egypt)", "ar_eg_female"),
    ("Swara (India)", "hi_warm_female"),
    ("Madhur (India)", "hi_friendly_male"),
    ("Emel (Turkey)", "tr_warm_female"),
    ("Ahmet (Turkey)", "tr_friendly_male"),
    ("Sofie (Sweden)", "sv_warm_female"),
    ("Mattias (Sweden)", "sv_friendly_male"),
    ("Christel (Denmark)", "da_warm_female"),
    ("Jeppe (Denmark)", "da_friendly_male"),
    ("Pernille (Norway)", "no_warm_female"),
    ("Finn (Norway)", "no_friendly_male"),
    ("Noora (Finland)", "fi_warm_female"),
    ("Harri (Finland)", "fi_friendly_male"),
    ("Vlasta (Czech)", "cs_warm_female"),
    ("Antonin (Czech)", "cs_friendly_male"),
    ("Athina (Greece)", "el_warm_female"),
    ("Nestoras (Greece)", "el_friendly_male"),
    ("Hila (Israel)", "he_warm_female"),
    ("Avri (Israel)", "he_friendly_male"),
    ("Noemi (Hungary)", "hu_warm_female"),
    ("Tamas (Hungary)", "hu_friendly_male"),
    ("Alina (Romania)", "ro_warm_female"),
    ("Emil (Romania)", "ro_friendly_male"),
    ("Polina (Ukraine)", "uk_warm_female"),
    ("Ostap (Ukraine)", "uk_friendly_male"),
]

AGE_CHOICES = [
    ("Toddler (2-3)", "toddler"),
    ("Preschool (3-5)", "preschool"),
    ("Early Reader (5-7)", "early_reader"),
    ("Older Kids (7+)", "older_kids"),
]


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
    theme: str,
    custom_theme: str,
    language: str,
    voice: str
):
    """Generate a personalized story and convert to audio."""

    # Validate inputs
    if not child_name or not child_name.strip():
        return "", None, "Please enter your child's name."

    # Clean name (letters, spaces, hyphens only)
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
                choices=AGE_CHOICES,
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
                choices=LANGUAGE_CHOICES,
                label="Story Language",
                value="en",
            )

            voice = gr.Dropdown(
                choices=VOICE_CHOICES,
                label="Voice",
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
        inputs=[child_name, age_group, theme, custom_theme, language, voice],
        outputs=[story_output, audio_output, status_output],
    )


if __name__ == "__main__":
    app.launch()
