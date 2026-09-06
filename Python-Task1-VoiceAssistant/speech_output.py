"""
speech_output.py
-----------------
Wraps pyttsx3 so the rest of the app has one simple function: speak(text).

Why wrap it?
    * pyttsx3 engines can be finicky (especially re-using one instance across
      multiple calls on some platforms), so we re-init defensively.
    * We want every spoken line to also be echoed to the terminal, and we
      want speech failures (no audio device, driver issues) to degrade to
      text-only output instead of crashing the app.
"""

import pyttsx3

from config import TTS_RATE, TTS_VOLUME


def _build_engine():
    """Create and configure a fresh pyttsx3 engine instance."""
    engine = pyttsx3.init()
    engine.setProperty("rate", TTS_RATE)
    engine.setProperty("volume", TTS_VOLUME)
    return engine


def speak(text: str) -> None:
    """
    Speak `text` aloud and print it to the terminal.

    Never raises: if the TTS engine is unavailable (missing audio driver,
    headless environment, etc.) we fall back to text-only output so the
    rest of the assistant keeps working.
    """
    print(f"Assistant: {text}")
    try:
        engine = _build_engine()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as error:
        # Text-only fallback — the user still sees the response.
        print(f"[speech_output] Voice output unavailable ({error}). "
              f"Continuing in text-only mode.")


def status(message: str) -> None:
    """Print a short status line like 'Listening...' without speaking it."""
    print(message)
