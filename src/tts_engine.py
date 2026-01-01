"""
Text-to-Speech engine using Microsoft Edge TTS.

Edge TTS is free, requires no API key, and provides high-quality neural voices.
Supports 90+ languages with 400+ voices.
"""

import asyncio
import tempfile
import os
from typing import Optional


# Supported languages with their locales and storytelling-appropriate voices
LANGUAGES = {
    "en": {
        "label": "English",
        "code": "en",
    },
    "es": {
        "label": "Español (Spanish)",
        "code": "es",
    },
    "fr": {
        "label": "Français (French)",
        "code": "fr",
    },
    "de": {
        "label": "Deutsch (German)",
        "code": "de",
    },
    "it": {
        "label": "Italiano (Italian)",
        "code": "it",
    },
    "pt": {
        "label": "Português (Portuguese)",
        "code": "pt",
    },
    "nl": {
        "label": "Nederlands (Dutch)",
        "code": "nl",
    },
    "pl": {
        "label": "Polski (Polish)",
        "code": "pl",
    },
    "ru": {
        "label": "Русский (Russian)",
        "code": "ru",
    },
    "ja": {
        "label": "日本語 (Japanese)",
        "code": "ja",
    },
    "zh": {
        "label": "中文 (Chinese)",
        "code": "zh",
    },
    "ko": {
        "label": "한국어 (Korean)",
        "code": "ko",
    },
    "ar": {
        "label": "العربية (Arabic)",
        "code": "ar",
    },
    "hi": {
        "label": "हिन्दी (Hindi)",
        "code": "hi",
    },
    "tr": {
        "label": "Türkçe (Turkish)",
        "code": "tr",
    },
    "sv": {
        "label": "Svenska (Swedish)",
        "code": "sv",
    },
    "da": {
        "label": "Dansk (Danish)",
        "code": "da",
    },
    "no": {
        "label": "Norsk (Norwegian)",
        "code": "no",
    },
    "fi": {
        "label": "Suomi (Finnish)",
        "code": "fi",
    },
    "cs": {
        "label": "Čeština (Czech)",
        "code": "cs",
    },
    "el": {
        "label": "Ελληνικά (Greek)",
        "code": "el",
    },
    "he": {
        "label": "עברית (Hebrew)",
        "code": "he",
    },
    "hu": {
        "label": "Magyar (Hungarian)",
        "code": "hu",
    },
    "ro": {
        "label": "Română (Romanian)",
        "code": "ro",
    },
    "uk": {
        "label": "Українська (Ukrainian)",
        "code": "uk",
    },
}


# Voice configurations organized by language - Microsoft Edge TTS voices
# These are warm, storytelling-appropriate voices for children
VOICES = {
    # English voices
    "en_warm_female_us": {
        "label": "🇺🇸 Warm Female (US)",
        "voice": "en-US-JennyNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "en",
    },
    "en_friendly_male_us": {
        "label": "🇺🇸 Friendly Male (US)",
        "voice": "en-US-GuyNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "en",
    },
    "en_friendly_male_uk": {
        "label": "🇬🇧 Friendly Male (UK)",
        "voice": "en-GB-RyanNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "en",
    },
    "en_storyteller_au": {
        "label": "🇦🇺 Storyteller (AU)",
        "voice": "en-AU-WilliamNeural",
        "rate": "-15%",
        "pitch": "-5Hz",
        "language": "en",
    },
    # Spanish voices
    "es_warm_female": {
        "label": "🇪🇸 Elvira (Spain)",
        "voice": "es-ES-ElviraNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "es",
    },
    "es_friendly_male": {
        "label": "🇪🇸 Alvaro (Spain)",
        "voice": "es-ES-AlvaroNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "es",
    },
    "es_mx_female": {
        "label": "🇲🇽 Dalia (Mexico)",
        "voice": "es-MX-DaliaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "es",
    },
    "es_mx_male": {
        "label": "🇲🇽 Jorge (Mexico)",
        "voice": "es-MX-JorgeNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "es",
    },
    # French voices
    "fr_warm_female": {
        "label": "🇫🇷 Denise (France)",
        "voice": "fr-FR-DeniseNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "fr",
    },
    "fr_friendly_male": {
        "label": "🇫🇷 Henri (France)",
        "voice": "fr-FR-HenriNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "fr",
    },
    "fr_ca_female": {
        "label": "🇨🇦 Sylvie (Canada)",
        "voice": "fr-CA-SylvieNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "fr",
    },
    # German voices
    "de_warm_female": {
        "label": "🇩🇪 Katja (Germany)",
        "voice": "de-DE-KatjaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "de",
    },
    "de_friendly_male": {
        "label": "🇩🇪 Conrad (Germany)",
        "voice": "de-DE-ConradNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "de",
    },
    "de_at_female": {
        "label": "🇦🇹 Ingrid (Austria)",
        "voice": "de-AT-IngridNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "de",
    },
    # Italian voices
    "it_warm_female": {
        "label": "🇮🇹 Elsa (Italy)",
        "voice": "it-IT-ElsaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "it",
    },
    "it_friendly_male": {
        "label": "🇮🇹 Diego (Italy)",
        "voice": "it-IT-DiegoNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "it",
    },
    # Portuguese voices
    "pt_br_female": {
        "label": "🇧🇷 Francisca (Brazil)",
        "voice": "pt-BR-FranciscaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "pt",
    },
    "pt_br_male": {
        "label": "🇧🇷 Antonio (Brazil)",
        "voice": "pt-BR-AntonioNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "pt",
    },
    "pt_pt_female": {
        "label": "🇵🇹 Raquel (Portugal)",
        "voice": "pt-PT-RaquelNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "pt",
    },
    # Dutch voices
    "nl_warm_female": {
        "label": "🇳🇱 Colette (Netherlands)",
        "voice": "nl-NL-ColetteNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "nl",
    },
    "nl_friendly_male": {
        "label": "🇳🇱 Maarten (Netherlands)",
        "voice": "nl-NL-MaartenNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "nl",
    },
    # Polish voices
    "pl_warm_female": {
        "label": "🇵🇱 Agnieszka (Poland)",
        "voice": "pl-PL-AgnieszkaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "pl",
    },
    "pl_friendly_male": {
        "label": "🇵🇱 Marek (Poland)",
        "voice": "pl-PL-MarekNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "pl",
    },
    # Russian voices
    "ru_warm_female": {
        "label": "🇷🇺 Svetlana (Russia)",
        "voice": "ru-RU-SvetlanaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ru",
    },
    "ru_friendly_male": {
        "label": "🇷🇺 Dmitry (Russia)",
        "voice": "ru-RU-DmitryNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ru",
    },
    # Japanese voices
    "ja_warm_female": {
        "label": "🇯🇵 Nanami (Japan)",
        "voice": "ja-JP-NanamiNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ja",
    },
    "ja_friendly_male": {
        "label": "🇯🇵 Keita (Japan)",
        "voice": "ja-JP-KeitaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ja",
    },
    # Chinese voices
    "zh_warm_female": {
        "label": "🇨🇳 Xiaoxiao (China)",
        "voice": "zh-CN-XiaoxiaoNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "zh",
    },
    "zh_friendly_male": {
        "label": "🇨🇳 Yunxi (China)",
        "voice": "zh-CN-YunxiNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "zh",
    },
    "zh_tw_female": {
        "label": "🇹🇼 Hsiao (Taiwan)",
        "voice": "zh-TW-HsiaoChenNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "zh",
    },
    # Korean voices
    "ko_warm_female": {
        "label": "🇰🇷 SunHi (Korea)",
        "voice": "ko-KR-SunHiNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ko",
    },
    "ko_friendly_male": {
        "label": "🇰🇷 InJoon (Korea)",
        "voice": "ko-KR-InJoonNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ko",
    },
    # Arabic voices
    "ar_warm_female": {
        "label": "🇸🇦 Zariyah (Saudi)",
        "voice": "ar-SA-ZariyahNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ar",
    },
    "ar_friendly_male": {
        "label": "🇸🇦 Hamed (Saudi)",
        "voice": "ar-SA-HamedNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ar",
    },
    "ar_eg_female": {
        "label": "🇪🇬 Salma (Egypt)",
        "voice": "ar-EG-SalmaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ar",
    },
    # Hindi voices
    "hi_warm_female": {
        "label": "🇮🇳 Swara (India)",
        "voice": "hi-IN-SwaraNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "hi",
    },
    "hi_friendly_male": {
        "label": "🇮🇳 Madhur (India)",
        "voice": "hi-IN-MadhurNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "hi",
    },
    # Turkish voices
    "tr_warm_female": {
        "label": "🇹🇷 Emel (Turkey)",
        "voice": "tr-TR-EmelNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "tr",
    },
    "tr_friendly_male": {
        "label": "🇹🇷 Ahmet (Turkey)",
        "voice": "tr-TR-AhmetNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "tr",
    },
    # Swedish voices
    "sv_warm_female": {
        "label": "🇸🇪 Sofie (Sweden)",
        "voice": "sv-SE-SofieNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "sv",
    },
    "sv_friendly_male": {
        "label": "🇸🇪 Mattias (Sweden)",
        "voice": "sv-SE-MattiasNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "sv",
    },
    # Danish voices
    "da_warm_female": {
        "label": "🇩🇰 Christel (Denmark)",
        "voice": "da-DK-ChristelNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "da",
    },
    "da_friendly_male": {
        "label": "🇩🇰 Jeppe (Denmark)",
        "voice": "da-DK-JeppeNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "da",
    },
    # Norwegian voices
    "no_warm_female": {
        "label": "🇳🇴 Pernille (Norway)",
        "voice": "nb-NO-PernilleNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "no",
    },
    "no_friendly_male": {
        "label": "🇳🇴 Finn (Norway)",
        "voice": "nb-NO-FinnNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "no",
    },
    # Finnish voices
    "fi_warm_female": {
        "label": "🇫🇮 Noora (Finland)",
        "voice": "fi-FI-NooraNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "fi",
    },
    "fi_friendly_male": {
        "label": "🇫🇮 Harri (Finland)",
        "voice": "fi-FI-HarriNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "fi",
    },
    # Czech voices
    "cs_warm_female": {
        "label": "🇨🇿 Vlasta (Czech)",
        "voice": "cs-CZ-VlastaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "cs",
    },
    "cs_friendly_male": {
        "label": "🇨🇿 Antonin (Czech)",
        "voice": "cs-CZ-AntoninNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "cs",
    },
    # Greek voices
    "el_warm_female": {
        "label": "🇬🇷 Athina (Greece)",
        "voice": "el-GR-AthinaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "el",
    },
    "el_friendly_male": {
        "label": "🇬🇷 Nestoras (Greece)",
        "voice": "el-GR-NestorasNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "el",
    },
    # Hebrew voices
    "he_warm_female": {
        "label": "🇮🇱 Hila (Israel)",
        "voice": "he-IL-HilaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "he",
    },
    "he_friendly_male": {
        "label": "🇮🇱 Avri (Israel)",
        "voice": "he-IL-AvriNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "he",
    },
    # Hungarian voices
    "hu_warm_female": {
        "label": "🇭🇺 Noemi (Hungary)",
        "voice": "hu-HU-NoemiNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "hu",
    },
    "hu_friendly_male": {
        "label": "🇭🇺 Tamas (Hungary)",
        "voice": "hu-HU-TamasNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "hu",
    },
    # Romanian voices
    "ro_warm_female": {
        "label": "🇷🇴 Alina (Romania)",
        "voice": "ro-RO-AlinaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ro",
    },
    "ro_friendly_male": {
        "label": "🇷🇴 Emil (Romania)",
        "voice": "ro-RO-EmilNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "ro",
    },
    # Ukrainian voices
    "uk_warm_female": {
        "label": "🇺🇦 Polina (Ukraine)",
        "voice": "uk-UA-PolinaNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "uk",
    },
    "uk_friendly_male": {
        "label": "🇺🇦 Ostap (Ukraine)",
        "voice": "uk-UA-OstapNeural",
        "rate": "-10%",
        "pitch": "+0Hz",
        "language": "uk",
    },
}

# Legacy voice mapping for backwards compatibility
LEGACY_VOICE_MAP = {
    "warm_female_us": "en_warm_female_us",
    "friendly_male_uk": "en_friendly_male_uk",
    "storyteller_au": "en_storyteller_au",
}


def get_voices_for_language(language_code: str) -> dict:
    """Get all voices available for a specific language.

    Args:
        language_code: The language code (e.g., 'en', 'es', 'fr').

    Returns:
        Dictionary of voice_key -> voice_config for the specified language.
    """
    return {
        k: v for k, v in VOICES.items()
        if v.get("language") == language_code
    }


def get_default_voice_for_language(language_code: str) -> str:
    """Get the default voice key for a language.

    Args:
        language_code: The language code.

    Returns:
        The default voice key for the language.
    """
    voices = get_voices_for_language(language_code)
    if voices:
        # Return first voice (usually warm female)
        return list(voices.keys())[0]
    # Fallback to English
    return "en_warm_female_us"


class TTSEngine:
    """Text-to-Speech engine using Microsoft Edge TTS."""

    def __init__(self):
        """Initialize the TTS engine."""
        pass  # edge-tts doesn't need initialization

    async def _generate_audio_async(
        self,
        text: str,
        voice: str = "en_warm_female_us",
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

        # Handle legacy voice keys for backwards compatibility
        if voice in LEGACY_VOICE_MAP:
            voice = LEGACY_VOICE_MAP[voice]

        voice_config = VOICES.get(voice, VOICES["en_warm_female_us"])

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
        voice: str = "en_warm_female_us",
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
        voice: str = "en_warm_female_us",
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
