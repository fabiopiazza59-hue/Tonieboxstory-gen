"""
Session-based rate limiting for story generation.
"""

from datetime import datetime, date
from typing import Tuple
import uuid


# Maximum stories per user per day
MAX_STORIES_PER_DAY = 10


class RateLimiter:
    """Simple session-based rate limiter.

    Uses Gradio's session state to track usage per user session.
    Note: This is session-based, not IP-based, so users can reset
    by clearing cookies. This is acceptable for a free service.
    """

    @staticmethod
    def get_initial_state() -> dict:
        """Get initial rate limiting state for a new session.

        Returns:
            Dictionary with rate limiting state.
        """
        return {
            "session_id": str(uuid.uuid4()),
            "stories_generated_today": 0,
            "last_generation_date": date.today().isoformat(),
        }

    @staticmethod
    def check_and_update(state: dict) -> Tuple[bool, int, str, dict]:
        """Check if user can generate a story and update state.

        Args:
            state: Current session state dictionary.

        Returns:
            Tuple of (allowed, remaining, message, updated_state)
        """
        if state is None:
            state = RateLimiter.get_initial_state()

        today = date.today().isoformat()

        # Reset counter if it's a new day
        if state.get("last_generation_date") != today:
            state["stories_generated_today"] = 0
            state["last_generation_date"] = today

        stories_today = state.get("stories_generated_today", 0)
        remaining = MAX_STORIES_PER_DAY - stories_today

        if stories_today >= MAX_STORIES_PER_DAY:
            return (
                False,
                0,
                f"You've created {MAX_STORIES_PER_DAY} stories today! "
                "Come back tomorrow for more magical adventures.",
                state
            )

        # Increment counter
        state["stories_generated_today"] = stories_today + 1
        remaining = MAX_STORIES_PER_DAY - stories_today - 1

        return (
            True,
            remaining,
            f"Story generated! You have {remaining} stories remaining today.",
            state
        )

    @staticmethod
    def get_remaining(state: dict) -> int:
        """Get remaining stories for today.

        Args:
            state: Current session state dictionary.

        Returns:
            Number of remaining stories.
        """
        if state is None:
            return MAX_STORIES_PER_DAY

        today = date.today().isoformat()

        # Reset if new day
        if state.get("last_generation_date") != today:
            return MAX_STORIES_PER_DAY

        stories_today = state.get("stories_generated_today", 0)
        return max(0, MAX_STORIES_PER_DAY - stories_today)

    @staticmethod
    def get_status_message(state: dict) -> str:
        """Get a friendly status message about remaining stories.

        Args:
            state: Current session state dictionary.

        Returns:
            Status message string.
        """
        remaining = RateLimiter.get_remaining(state)

        if remaining == 0:
            return "No stories remaining today. Come back tomorrow!"
        elif remaining == 1:
            return "1 story remaining today"
        elif remaining == MAX_STORIES_PER_DAY:
            return f"Welcome! You can create up to {MAX_STORIES_PER_DAY} stories today."
        else:
            return f"{remaining} stories remaining today"
