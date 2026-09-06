"""
reminder.py
------------
Threaded reminders so the assistant keeps listening/responding while a
reminder timer counts down in the background.

Duration parsing supports simple natural phrases like:
    "10 minutes", "1 hour", "30 seconds", "2 hours and 15 minutes"
"""

import re
import threading
import time

_UNIT_SECONDS = {
    "second": 1, "seconds": 1, "sec": 1, "secs": 1,
    "minute": 60, "minutes": 60, "min": 60, "mins": 60,
    "hour": 3600, "hours": 3600, "hr": 3600, "hrs": 3600,
}

_NUMBER_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def parse_duration(text: str) -> int | None:
    """
    Parse a natural-language duration like "10 minutes" or "an hour" into
    a number of seconds. Returns None if it can't be parsed.
    """
    if not text:
        return None

    text = text.lower().strip()
    total_seconds = 0
    found_any = False

    # Matches things like "10 minutes", "2 hours", "an hour"
    for match in re.finditer(
        r"(?P<number>\d+|[a-z]+)\s*(?P<unit>seconds?|secs?|minutes?|mins?|hours?|hrs?)",
        text,
    ):
        number_raw = match.group("number")
        unit = match.group("unit")

        number = _NUMBER_WORDS.get(number_raw)
        if number is None:
            try:
                number = int(number_raw)
            except ValueError:
                continue

        unit_seconds = _UNIT_SECONDS.get(unit)
        if unit_seconds is None:
            continue

        total_seconds += number * unit_seconds
        found_any = True

    return total_seconds if found_any and total_seconds > 0 else None


def schedule_reminder(seconds: int, task_description: str, on_fire) -> None:
    """
    Schedule a reminder that calls `on_fire(task_description)` after
    `seconds` have elapsed, without blocking the caller.
    """

    def _wait_and_fire():
        time.sleep(seconds)
        on_fire(task_description)

    timer_thread = threading.Thread(target=_wait_and_fire, daemon=True)
    timer_thread.start()
