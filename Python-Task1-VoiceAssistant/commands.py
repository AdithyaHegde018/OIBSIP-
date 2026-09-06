"""
commands.py
------------
The dispatcher. Takes a detected intent (from intent_handler) plus the
raw spoken text, and routes it to the right feature module.

This is the only module that "knows about" every other feature module —
keeps main.py thin and each feature module independent/testable.
"""

import webbrowser
from datetime import datetime

import speech_output
import voice_input
from intent_handler import detect_intent
from weather import get_weather
from email_service import run_email_flow
from reminder import parse_duration, schedule_reminder
from knowledge import answer_question
from custom_commands import match_custom_command, execute_custom_command
from config import GREETING_TEXT, EXIT_WORDS

_WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "linkedin": "https://www.linkedin.com",
}


def handle_command(text: str, custom_commands: dict) -> bool:
    """
    Process one piece of recognized (or typed) text.

    Returns False if the assistant should exit, True otherwise.
    """
    if not text:
        speech_output.speak("Sorry, I didn't catch that. Could you say it again?")
        return True

    # Custom commands take priority so users can override anything.
    custom_url = match_custom_command(text, custom_commands)
    if custom_url:
        speech_output.status("Opening custom command...")
        speech_output.speak(execute_custom_command(custom_url))
        return True

    result = detect_intent(text)
    intent = result["intent"]
    entities = result["entities"]

    if intent == "exit" or text.strip() in EXIT_WORDS:
        speech_output.speak("Goodbye! Have a great day.")
        return False

    if intent == "greeting":
        speech_output.speak(GREETING_TEXT)

    elif intent == "time":
        now = datetime.now().strftime("%I:%M %p")
        speech_output.speak(f"The current time is {now}.")

    elif intent == "date":
        today = datetime.now().strftime("%A, %B %d, %Y")
        speech_output.speak(f"Today's date is {today}.")

    elif intent == "weather":
        city = entities.get("city", "").strip()
        speech_output.status("Fetching weather...")
        speech_output.speak(get_weather(city))

    elif intent == "reminder":
        _handle_reminder(entities)

    elif intent == "email":
        speech_output.status("Sending email...")
        result_message = run_email_flow(voice_input.listen, speech_output.speak)
        speech_output.speak(result_message)

    elif intent == "open_website":
        site = entities.get("site", "").strip()
        url = _WEBSITES.get(site)
        if url:
            speech_output.status("Searching...")
            webbrowser.open(url)
            speech_output.speak(f"Opening {site.capitalize()}.")
        else:
            speech_output.speak(f"I don't know how to open {site}.")

    elif intent == "web_search":
        query = entities.get("query", "").strip()
        if query:
            speech_output.status("Searching...")
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            speech_output.speak(f"Searching the web for {query}.")
        else:
            speech_output.speak("What would you like me to search for?")

    elif intent == "knowledge":
        question = entities.get("question", text)
        speech_output.speak(answer_question(question))

    else:
        speech_output.speak(
            "I'm not sure how to help with that yet. You can ask me about "
            "the time, date, weather, reminders, email, or a web search."
        )

    return True


def _handle_reminder(entities: dict) -> None:
    """Parse and schedule a reminder, asking for a task if needed."""
    duration_text = entities.get("duration", "")
    seconds = parse_duration(duration_text)

    if seconds is None:
        speech_output.speak(
            "I couldn't understand the reminder duration. "
            "Please say something like 'remind me after 10 minutes'."
        )
        return

    task = entities.get("task")
    if not task:
        speech_output.speak("What should I remind you about?")
        task = voice_input.listen() or "your reminder"

    speech_output.speak(f"Reminder scheduled for {duration_text.strip()} from now.")

    def _on_fire(task_description: str) -> None:
        speech_output.speak(f"Reminder: {task_description}")

    schedule_reminder(seconds, task, _on_fire)
