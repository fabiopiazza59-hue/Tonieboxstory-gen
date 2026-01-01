"""
Personalized Story Generator - Main Application

A free SaaS for generating personalized audio stories for Toniebox Creative-Tonies.
"""

import gradio as gr
from typing import Tuple, Optional, Any

from src.story_generator import StoryGenerator
from src.tts_engine import TTSEngine, VOICES
from src.rate_limiter import RateLimiter, MAX_STORIES_PER_DAY
from src.prompts import AGE_GROUPS, THEMES


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


def generate_story_and_audio(
    child_name: str,
    age_group: str,
    theme: str,
    custom_theme: str,
    voice: str,
    stories_count: int,
    progress=gr.Progress()
):
    """Generate a personalized story and convert to audio."""

    # Validate inputs
    if not child_name or not child_name.strip():
        return "", None, "⚠️ Please enter your child's name.", "", stories_count, gr.update(visible=False), gr.update(visible=False)

    # Clean name (letters, spaces, hyphens only)
    clean_name = "".join(c for c in child_name if c.isalpha() or c in " -'")
    if not clean_name:
        return "", None, "⚠️ Please enter a valid name (letters only).", "", stories_count, gr.update(visible=False), gr.update(visible=False)

    # Check rate limit
    if stories_count >= MAX_STORIES_PER_DAY:
        return "", None, f"⚠️ You've created {MAX_STORIES_PER_DAY} stories today! Come back tomorrow.", "", stories_count, gr.update(visible=False), gr.update(visible=False)

    # Determine theme
    final_theme = custom_theme.strip() if theme == "Custom" else theme
    if not final_theme:
        return "", None, "⚠️ Please select a theme or enter a custom theme.", "", stories_count, gr.update(visible=False), gr.update(visible=False)

    try:
        # Step 1: Generate story
        progress(0.1, desc="✨ Creating your magical story...")
        generator = get_story_generator()
        story_text = generator.generate_story(
            child_name=clean_name,
            age_group=age_group,
            theme=final_theme
        )

        # Step 2: Generate audio
        progress(0.5, desc="🎙️ Recording with a wonderful voice...")
        tts = get_tts_engine()
        audio_path = tts.generate_audio(
            text=story_text,
            voice=voice,
            output_format="mp3"
        )

        progress(1.0, desc="✅ Done!")

        # Calculate estimated duration
        duration_min = generator.estimate_duration(story_text)
        duration_str = f"{int(duration_min)} min {int((duration_min % 1) * 60)} sec"

        # Update count
        new_count = stories_count + 1
        remaining = MAX_STORIES_PER_DAY - new_count

        status_msg = (
            f"✅ **Story created for {clean_name}!**\n\n"
            f"📖 Duration: ~{duration_str}\n"
            f"📊 {remaining} stories remaining today"
        )

        return story_text, audio_path, status_msg, "", new_count, gr.update(visible=True), gr.update(visible=True)

    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "GROQ_API_KEY" in error_msg:
            error_msg = "Service temporarily unavailable. Please try again later."
        return "", None, f"❌ Oops! {error_msg}", "", stories_count, gr.update(visible=False), gr.update(visible=False)


def handle_feedback(feedback_type: str) -> str:
    """Handle thumbs up/down feedback."""
    if feedback_type == "up":
        return "💜 Thank you! We're glad you enjoyed the story."
    else:
        return "💜 Thank you for your feedback!"


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

    # Hidden counter for rate limiting
    stories_count = gr.State(value=0)

    # Header
    gr.Markdown(
        """
        # 📖 Personalized Story Generator

        Create magical bedtime stories for your child's **Toniebox Creative-Tonie**!

        Simply enter your child's name, pick a theme, and we'll generate a unique story
        with audio ready to upload to your Creative-Tonie.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎨 Story Details")

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

            voice = gr.Radio(
                choices=[(v["label"], k) for k, v in VOICES.items()],
                label="Voice",
                value="warm_female_us",
            )

            generate_btn = gr.Button(
                "🎭 Generate Story",
                variant="primary",
                size="lg",
            )

            gr.Markdown(f"*You can create up to {MAX_STORIES_PER_DAY} stories per day*")

        with gr.Column(scale=1):
            gr.Markdown("### 📚 Your Story")

            status_output = gr.Markdown(
                value="👆 Enter details and click 'Generate Story' to begin!"
            )

            story_output = gr.Textbox(
                label="Story Preview",
                lines=10,
                max_lines=15,
                interactive=False,
            )

            audio_output = gr.Audio(
                label="🔊 Listen to Your Story",
                type="filepath",
            )

            with gr.Row():
                feedback_msg = gr.Markdown("")
                thumbs_up = gr.Button("👍", visible=False, min_width=60)
                thumbs_down = gr.Button("👎", visible=False, min_width=60)

    gr.Markdown(
        """
        ---
        ### 📱 How to Use Your Story

        1. **Download** the MP3 file using the download button on the audio player
        2. **Open** [my.tonies.com](https://my.tonies.com) or the **mytonies app**
        3. **Upload** the MP3 to your Creative-Tonie
        4. **Place** the Creative-Tonie on your Toniebox to sync
        5. **Enjoy** your personalized story!

        ---
        *Made with 💜 for little dreamers everywhere*
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
        inputs=[child_name, age_group, theme, custom_theme, voice, stories_count],
        outputs=[story_output, audio_output, status_output, feedback_msg, stories_count, thumbs_up, thumbs_down],
    )

    thumbs_up.click(
        fn=lambda: handle_feedback("up"),
        outputs=[feedback_msg],
    )

    thumbs_down.click(
        fn=lambda: handle_feedback("down"),
        outputs=[feedback_msg],
    )


if __name__ == "__main__":
    app.launch()
