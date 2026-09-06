"""
custom_commands.py
--------------------
Loads user-defined commands from custom_commands.json and matches spoken
text against them, without hard-coding any specific command in the source.

Format of custom_commands.json:
    { "spoken phrase": "https://url-to-open.com" }

Matching is a simple substring check (case-insensitive) against the
phrase the user spoke — good enough for a fixed, user-curated list, and
much safer than eval()-based execution.
"""

import json
import webbrowser

from config import CUSTOM_COMMANDS_FILE


def load_custom_commands() -> dict:
    """
    Load custom commands from JSON. Returns an empty dict (instead of
    raising) if the file is missing or malformed, so the app keeps running.
    """
    try:
        with open(CUSTOM_COMMANDS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return {key.lower(): value for key, value in data.items()}
            return {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as error:
        print(f"[custom_commands] Could not parse custom_commands.json: {error}")
        return {}


def match_custom_command(text: str, commands: dict) -> str | None:
    """
    Return the URL for the custom command phrase found in `text`.

    Phrases are checked longest-first so a more specific phrase like
    "open github repositories" is matched in preference to a shorter
    phrase it contains, like "open github".
    """
    for phrase in sorted(commands, key=len, reverse=True):
        if phrase in text:
            return commands[phrase]
    return None


def execute_custom_command(url: str) -> str:
    """Open the given URL in the default browser. Never raises."""
    try:
        webbrowser.open(url)
        return f"Opening {url}"
    except Exception as error:
        return f"I couldn't open that link: {error}"
