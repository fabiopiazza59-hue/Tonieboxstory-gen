"""
Personalized Story Generator - Main Application

A free SaaS for generating personalized audio stories for Toniebox Creative-Tonies.
"""

import os
import gradio as gr
from typing import Tuple, Optional

from src.story_generator import StoryGenerator
from src.tts_engine import TTSEngine, get_available_voices, VOICES
from src.rate_limiter import RateLimiter, MAX_STORIES_PER_DAY
from src.prompts import AGE_GROUPS, THEMES


# Initialize components
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
        tts_engine = TTSEngine(device="cpu")
    return tts_engine


def generate_story_and_audio(
    child_name: str,
    age_group: str,
    theme: str,
    custom_theme: str,
    voice: str,
    state: dict,
    progress=gr.Progress()
) -> Tuple[str, Optional[str], str, str, dict, gr.update, gr.update]:
    """Generate a personalized story and convert to audio.

    Args:
        child_name: Child's name for the story.
        age_group: Age group key.
        theme: Selected theme or "Custom".
        custom_theme: Custom theme text if theme is "Custom".
        voice: Voice key.
        state: Session state for rate limiting.
        progress: Gradio progress tracker.

    Returns:
        Tuple of (story_text, audio_path, status, feedback_msg, state, thumbs_up_update, thumbs_down_update)
    """
    # Initialize state if needed
    if state is None:
        state = RateLimiter.get_initial_state()

    # Validate inputs
    if not child_name or not child_name.strip():
        return (
            "",
            None,
            "Please enter your child's name.",
            "",
            state,
            gr.update(visible=False),
            gr.update(visible=False)
        )

    # Clean name (letters, spaces, hyphens only)
    clean_name = "".join(c for c in child_name if c.isalpha() or c in " -'")
    if not clean_name:
        return (
            "",
            None,
            "Please enter a valid name (letters only).",
            "",
            state,
            gr.update(visible=False),
            gr.update(visible=False)
        )

    # Check rate limit
    allowed, remaining, limit_msg, state = RateLimiter.check_and_update(state)
    if not allowed:
        return (
            "",
            None,
            limit_msg,
            "",
            state,
            gr.update(visible=False),
            gr.update(visible=False)
        )

    # Determine theme
    final_theme = custom_theme.strip() if theme == "Custom" else theme
    if not final_theme:
        return (
            "",
            None,
            "Please select a theme or enter a custom theme.",
            "",
            state,
            gr.update(visible=False),
            gr.update(visible=False)
        )

    try:
        # Step 1: Generate story
        progress(0.1, desc="Creating your magical story...")
        generator = get_story_generator()
        story_text = generator.generate_story(
            child_name=clean_name,
            age_group=age_group,
            theme=final_theme
        )

        # Step 2: Generate audio
        progress(0.4, desc="Recording the story with a wonderful voice...")
        tts = get_tts_engine()

        # Use chunked generation for longer stories
        word_count = len(story_text.split())
        if word_count > 500:
            audio_path = tts.generate_audio_chunks(
                text=story_text,
                voice=voice,
                chunk_size=800,
                output_format="mp3"
            )
        else:
            audio_path = tts.generate_audio(
                text=story_text,
                voice=voice,
                output_format="mp3"
            )

        progress(1.0, desc="Done!")

        # Calculate estimated duration
        duration_min = generator.estimate_duration(story_text)
        duration_str = f"{int(duration_min)} min {int((duration_min % 1) * 60)} sec"

        status_msg = (
            f"Story created for {clean_name}! "
            f"Duration: ~{duration_str}. "
            f"You have {remaining} stories remaining today."
        )

        return (
            story_text,
            audio_path,
            status_msg,
            "",
            state,
            gr.update(visible=True),
            gr.update(visible=True)
        )

    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg:
            error_msg = "Service temporarily unavailable. Please try again later."
        return (
            "",
            None,
            f"Oops! Something went wrong: {error_msg}",
            "",
            state,
            gr.update(visible=False),
            gr.update(visible=False)
        )


def handle_feedback(feedback_type: str, story_text: str) -> str:
    """Handle thumbs up/down feedback.

    Args:
        feedback_type: 'up' or 'down'
        story_text: The story that was rated

    Returns:
        Feedback confirmation message
    """
    # In a production app, you'd log this to a database
    # For now, just acknowledge the feedback
    if feedback_type == "up":
        return "Thank you! We're glad you enjoyed the story."
    else:
        return "Thank you for your feedback. We'll work on making better stories!"


def update_custom_theme_visibility(theme: str) -> gr.update:
    """Show/hide custom theme input based on theme selection."""
    return gr.update(visible=(theme == "Custom"))


def get_remaining_stories_text(state: dict) -> str:
    """Get remaining stories text for display."""
    remaining = RateLimiter.get_remaining(state)
    if remaining == MAX_STORIES_PER_DAY:
        return f"You can create up to {MAX_STORIES_PER_DAY} stories today"
    elif remaining == 0:
        return "No stories remaining today. Come back tomorrow!"
    else:
        return f"{remaining} stories remaining today"


# Build the Gradio interface
def create_app():
    """Create and configure the Gradio application."""

    # Theme choices
    theme_choices = THEMES + ["Custom"]

    # Age group choices (label -> key mapping)
    age_choices = [(v["label"], k) for k, v in AGE_GROUPS.items()]

    # Voice choices
    voice_choices = [(v["label"], k) for k, v in VOICES.items()]

    with gr.Blocks(
        title="Personalized Story Generator",
        theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="pink",
        ),
        css="""
        .story-box {
            max-height: 300px;
            overflow-y: auto;
        }
        .feedback-btn {
            min-width: 60px !important;
        }
        """
    ) as app:

        # Session state for rate limiting
        state = gr.State(RateLimiter.get_initial_state())

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
                # Input section
                gr.Markdown("### Story Details")

                child_name = gr.Textbox(
                    label="Child's Name",
                    placeholder="Enter your child's name...",
                    max_lines=1,
                )

                age_group = gr.Radio(
                    choices=age_choices,
                    label="Age Group",
                    value="preschool",
                )

                theme = gr.Dropdown(
                    choices=theme_choices,
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
                    choices=voice_choices,
                    label="Voice",
                    value="warm_female_us",
                )

                generate_btn = gr.Button(
                    "Generate Story",
                    variant="primary",
                    size="lg",
                )

                remaining_text = gr.Markdown(
                    value=f"You can create up to {MAX_STORIES_PER_DAY} stories today"
                )

            with gr.Column(scale=1):
                # Output section
                gr.Markdown("### Your Story")

                status_output = gr.Markdown(
                    value="Enter details and click 'Generate Story' to begin!",
                    elem_classes=["status-box"]
                )

                story_output = gr.Textbox(
                    label="Story Preview",
                    lines=10,
                    max_lines=15,
                    interactive=False,
                    elem_classes=["story-box"],
                )

                audio_output = gr.Audio(
                    label="Listen to Your Story",
                    type="filepath",
                )

                # Feedback section
                with gr.Row():
                    feedback_msg = gr.Markdown("")

                    thumbs_up = gr.Button(
                        "👍",
                        visible=False,
                        elem_classes=["feedback-btn"],
                        min_width=60,
                    )
                    thumbs_down = gr.Button(
                        "👎",
                        visible=False,
                        elem_classes=["feedback-btn"],
                        min_width=60,
                    )

        # Instructions footer
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
            inputs=[child_name, age_group, theme, custom_theme, voice, state],
            outputs=[story_output, audio_output, status_output, feedback_msg, state, thumbs_up, thumbs_down],
        )

        thumbs_up.click(
            fn=lambda story: handle_feedback("up", story),
            inputs=[story_output],
            outputs=[feedback_msg],
        )

        thumbs_down.click(
            fn=lambda story: handle_feedback("down", story),
            inputs=[story_output],
            outputs=[feedback_msg],
        )

    return app


# Create and launch the app
app = create_app()

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
