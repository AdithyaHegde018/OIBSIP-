"""
config.py
---------
Central configuration for the voice assistant.

Responsibilities:
    * Load environment variables from a .env file (never hard-code secrets).
    * Expose typed, ready-to-use constants for the rest of the app.
    * Fail loudly (but gracefully) if something *required* is missing, while
      still letting the assistant run in a degraded mode when possible
      (e.g. weather/email features disabled if their keys are absent).

No other module should call os.getenv() directly — everything funnels
through here so there is a single source of truth for configuration.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present.
load_dotenv()


def _get_env(key: str, default: str | None = None) -> str | None:
    """Small wrapper around os.getenv for consistency/testability."""
    value = os.getenv(key, default)
    return value if value not in ("", None) else default


# ---------------------------------------------------------------------------
# Weather (OpenWeatherMap)
# ---------------------------------------------------------------------------
OPENWEATHER_API_KEY = _get_env("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_ENABLED = OPENWEATHER_API_KEY is not None

# ---------------------------------------------------------------------------
# Email (SMTP)
# ---------------------------------------------------------------------------
EMAIL_ADDRESS = _get_env("EMAIL_ADDRESS")
EMAIL_PASSWORD = _get_env("EMAIL_PASSWORD")  # App password, not real password
SMTP_SERVER = _get_env("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(_get_env("SMTP_PORT", "587"))
EMAIL_ENABLED = EMAIL_ADDRESS is not None and EMAIL_PASSWORD is not None

# ---------------------------------------------------------------------------
# General knowledge API (optional — DuckDuckGo Instant Answer, no key needed)
# ---------------------------------------------------------------------------
KNOWLEDGE_API_URL = "https://api.duckduckgo.com/"

# ---------------------------------------------------------------------------
# Assistant behaviour / text
# ---------------------------------------------------------------------------
ASSISTANT_NAME = "Assistant"
GREETING_TEXT = "Hello! How can I help you?"
EXIT_WORDS = {"exit", "quit", "stop", "goodbye", "bye"}

# ---------------------------------------------------------------------------
# File locations
# ---------------------------------------------------------------------------
CUSTOM_COMMANDS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "custom_commands.json"
)

# ---------------------------------------------------------------------------
# Speech engine tuning
# ---------------------------------------------------------------------------
TTS_RATE = 175          # words per minute
TTS_VOLUME = 1.0        # 0.0 - 1.0
LISTEN_TIMEOUT = 5       # seconds to wait for phrase to start
PHRASE_TIME_LIMIT = 8    # max seconds for a single phrase
