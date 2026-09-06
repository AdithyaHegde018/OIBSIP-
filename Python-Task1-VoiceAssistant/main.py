"""
main.py
--------
Entry point for the Python Voice Assistant.

Responsibilities:
    * Print the banner / greeting.
    * Load custom commands once at startup.
    * Run the main listen -> process -> respond loop.
    * Fall back to typed input automatically if voice keeps failing, so a
      broken microphone never makes the whole app unusable.
"""

import sys

import speech_output
import voice_input
from commands import handle_command
from custom_commands import load_custom_commands
from config import GREETING_TEXT

MAX_CONSECUTIVE_VOICE_FAILURES = 3


def print_banner() -> None:
    print("=" * 50)
    print("          PYTHON VOICE ASSISTANT")
    print("=" * 50)


def main() -> None:
    print_banner()
    speech_output.speak(GREETING_TEXT)

    try:
        custom_commands = load_custom_commands()
    except Exception as error:
        print(f"[main] Could not load custom commands: {error}")
        custom_commands = {}

    consecutive_failures = 0
    use_typed_input = False

    while True:
        try:
            if use_typed_input:
                text = voice_input.listen_typed_fallback()
            else:
                text = voice_input.listen()

            if text is None:
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_VOICE_FAILURES and not use_typed_input:
                    speech_output.speak(
                        "I'm having trouble hearing you. Switching to typed "
                        "input — just type your commands instead."
                    )
                    use_typed_input = True
                    consecutive_failures = 0
                continue

            consecutive_failures = 0
            print(f"You: {text}")

            keep_running = handle_command(text, custom_commands)
            if not keep_running:
                break

        except KeyboardInterrupt:
            speech_output.speak("Goodbye! Have a great day.")
            break
        except Exception as error:
            # Catch-all safety net: log and keep the assistant alive.
            print(f"[main] Unexpected error: {error}")
            speech_output.speak("Something went wrong, but I'm still here. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except Exception as fatal_error:
        print(f"[main] Fatal error, shutting down: {fatal_error}")
        sys.exit(1)
