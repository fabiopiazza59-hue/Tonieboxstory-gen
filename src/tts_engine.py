"""
Text-to-Speech engine using Microsoft Edge TTS.

Edge TTS is free, requires no API key, and provides high-quality neural voices.
"""

import asyncio
import tempfile
import os
from typing import Optional


# Voice configurations - Microsoft Edge TTS voices
# These are warm, storytelling-appropriate voices
VOICES = {
    "warm_female_us": {
        "label": "Warm Female (US)",
        "voice": "en-US-JennyNeural",
        "rate": "-10%",  # Slightly slower for bedtime stories
        "pitch": "+0Hz",
    },
    "friendly_male_uk": {
        "label": "Friendly Male (UK)",
        "voice": "en-GB-RyanNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
    },
    "storyteller_au": {
        "label": "Storyteller (AU)",
        "voice": "en-AU-WilliamNeural",
        "rate": "-15%",  # Even slower, more dramatic
        "pitch": "-5Hz",
    },
}


class TTSEngine:
    """Text-to-Speech engine using Microsoft Edge TTS."""

    def __init__(self):
        """Initialize the TTS engine."""
        pass  # edge-tts doesn't need initialization

    async def _generate_audio_async(
        self,
        text: str,
        voice: str = "warm_female_us",
        output_format: str = "mp3",
    ) -> str:
        """Async method to generate audio from text.

        Args:
            text: The text to convert to speech.
            voice: Voice key from VOICES dict.
            output_format: Output format ('mp3' or 'wav').

        Returns:
            Path to the generated audio file.
        """
        import edge_tts

        voice_config = VOICES.get(voice, VOICES["warm_female_us"])

        # Create temp file for output
        suffix = f".{output_format}"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            output_path = f.name

        # Create communicate instance
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_config["voice"],
            rate=voice_config["rate"],
            pitch=voice_config["pitch"],
        )

        # Generate audio
        await communicate.save(output_path)

        return output_path

    def generate_audio(
        self,
        text: str,
        voice: str = "warm_female_us",
        output_format: str = "mp3",
    ) -> str:
        """Generate audio from text (synchronous wrapper).

        Args:
            text: The text to convert to speech.
            voice: Voice key from VOICES dict.
            output_format: Output format ('mp3').

        Returns:
            Path to the generated audio file.
        """
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._generate_audio_async(text, voice, output_format)
            )
        finally:
            loop.close()

    def generate_audio_chunks(
        self,
        text: str,
        voice: str = "warm_female_us",
        chunk_size: int = 2000,
        output_format: str = "mp3",
    ) -> str:
        """Generate audio from long text by processing in chunks.

        Edge TTS handles long text well, but we chunk for reliability.

        Args:
            text: The text to convert to speech.
            voice: Voice key from VOICES dict.
            chunk_size: Approximate characters per chunk.
            output_format: Output format ('mp3').

        Returns:
            Path to the generated audio file.
        """
        # Edge TTS handles long text well, so we can often skip chunking
        if len(text) <= 5000:
            return self.generate_audio(text, voice, output_format)

        # Split text into chunks at sentence boundaries
        chunks = self._split_into_chunks(text, chunk_size)

        if len(chunks) == 1:
            return self.generate_audio(text, voice, output_format)

        # Generate audio for each chunk
        audio_files = []
        for chunk in chunks:
            chunk_path = self.generate_audio(chunk, voice, output_format)
            audio_files.append(chunk_path)

        # Concatenate all chunks
        output_path = self._concatenate_audio(audio_files, output_format)

        # Clean up chunk files
        for f in audio_files:
            if os.path.exists(f):
                os.unlink(f)

        return output_path

    def _split_into_chunks(self, text: str, chunk_size: int) -> list:
        """Split text into chunks at sentence boundaries.

        Args:
            text: Text to split.
            chunk_size: Approximate characters per chunk.

        Returns:
            List of text chunks.
        """
        sentences = []
        current = ""

        # Simple sentence splitting
        for char in text:
            current += char
            if char in ".!?" and len(current) > 10:
                sentences.append(current.strip())
                current = ""

        if current.strip():
            sentences.append(current.strip())

        # Group sentences into chunks
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _concatenate_audio(self, audio_files: list, output_format: str) -> str:
        """Concatenate multiple audio files into one.

        Args:
            audio_files: List of paths to audio files.
            output_format: Output format.

        Returns:
            Path to concatenated audio file.
        """
        from pydub import AudioSegment

        combined = AudioSegment.empty()
        for f in audio_files:
            audio = AudioSegment.from_mp3(f)
            combined += audio

        suffix = f".{output_format}"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as out_file:
            output_path = out_file.name

        combined.export(output_path, format=output_format, bitrate="192k")

        return output_path


def get_available_voices() -> dict:
    """Get available voices for the UI.

    Returns:
        Dictionary of voice_key -> label.
    """
    return {k: v["label"] for k, v in VOICES.items()}


async def list_all_voices():
    """List all available Edge TTS voices (for development/debugging).

    Returns:
        List of available voices.
    """
    import edge_tts
    voices = await edge_tts.list_voices()
    return voices
