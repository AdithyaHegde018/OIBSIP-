"""
voice_input.py
----------------
Handles microphone capture and speech-to-text conversion using the
SpeechRecognition library (Google Web Speech API backend by default).

Every failure mode is caught here so callers only ever get back either:
    * a lowercase string with what the user said, or
    * None (meaning: could not understand / no mic / no network — caller
      should just prompt again, not crash).
"""

import speech_recognition as sr

from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT
from speech_output import status


def _get_recognizer_and_mic():
    """
    Try to build a Recognizer + Microphone pair.
    Returns (recognizer, microphone) or (recognizer, None) if no mic exists.
    """
    recognizer = sr.Recognizer()
    try:
        microphone = sr.Microphone()
    except OSError as error:
        status(f"[voice_input] No microphone detected: {error}")
        microphone = None
    return recognizer, microphone


def listen() -> str | None:
    """
    Capture one spoken phrase from the default microphone and transcribe it.

    Returns the recognized text in lowercase, or None if:
        * no microphone is available,
        * nothing was said within the timeout,
        * the speech could not be understood,
        * the speech recognition service is unreachable.
    """
    recognizer, microphone = _get_recognizer_and_mic()

    if microphone is None:
        return None

    try:
        with microphone as source:
            status("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=LISTEN_TIMEOUT,
                phrase_time_limit=PHRASE_TIME_LIMIT,
            )
    except sr.WaitTimeoutError:
        status("[voice_input] No speech detected in time.")
        return None
    except OSError as error:
        status(f"[voice_input] Microphone error: {error}")
        return None

    try:
        status("Processing...")
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.UnknownValueError:
        status("[voice_input] Could not understand the audio.")
        return None
    except sr.RequestError as error:
        status(f"[voice_input] Speech recognition service unavailable: {error}")
        return None


def listen_typed_fallback(prompt: str = "You: ") -> str:
    """
    Text-input fallback for environments without a working microphone
    (useful for testing, or when voice input keeps failing).
    """
    return input(prompt).strip().lower()
