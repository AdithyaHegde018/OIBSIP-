"""
intent_handler.py
-------------------
Lightweight, dependency-free intent detection.

Rather than pulling in a heavy NLP stack, this module uses:
    * A set of regex/keyword *patterns per intent* (so "what time is it",
      "can you tell me the current time", and "tell me the time" all map
      to the same TIME intent), and
    * Simple entity extraction (city names, durations, search queries)
      via regex groups.

This keeps the project lightweight while still avoiding naive single-
keyword matching, satisfying the "no exact keyword matching only" rule.

Returns a dict: {"intent": <str>, "entities": {<str>: <str>, ...}}
The special intent "unknown" means nothing matched.
"""

import re

# Ordered list of (intent_name, [regex patterns]).
# Order matters: more specific patterns should come before generic ones.
_INTENT_PATTERNS = [
    ("greeting", [
        r"\bhello\b", r"\bhi\b", r"\bhey\b", r"good (morning|afternoon|evening)",
    ]),
    ("exit", [
        r"\b(exit|quit|stop|goodbye|bye)\b",
    ]),
    ("time", [
        r"what.?s the time", r"current time", r"tell me the time",
        r"what time is it",
    ]),
    ("date", [
        r"what.?s the date", r"current date", r"tell me the date",
        r"what.s today.?s date", r"what day is it",
    ]),
    ("weather", [
        r"weather (in|at|for) (?P<city>[a-zA-Z\s]+)",
        r"(temperature|forecast) (in|at|for) (?P<city>[a-zA-Z\s]+)",
        r"what.?s the weather like in (?P<city>[a-zA-Z\s]+)",
    ]),
    ("reminder", [
        r"remind me (after|in) (?P<duration>[\w\s]+?)(?: to (?P<task>.+))?$",
        r"set a reminder (for|after|in) (?P<duration>[\w\s]+?)(?: to (?P<task>.+))?$",
    ]),
    ("email", [
        r"send (an |a )?email",
        r"compose (an |a )?email",
    ]),
    ("open_website", [
        r"open (?P<site>google|youtube|github|linkedin)",
    ]),
    ("web_search", [
        r"search (the internet |the web )?for (?P<query>.+)",
        r"look ?up (?P<query>.+)",
        r"google (?P<query>.+)",
    ]),
    ("knowledge", [
        r"^(what|who|where|when|why|how) (is|are|was|were) (?P<question>.+)",
        r"^do you know (?P<question>.+)",
    ]),
]


def detect_intent(text: str) -> dict:
    """
    Analyze `text` (already lowercased) and return the best-matching intent
    along with any extracted entities.
    """
    if not text:
        return {"intent": "unknown", "entities": {}}

    cleaned = text.strip()

    for intent_name, patterns in _INTENT_PATTERNS:
        for pattern in patterns:
            match = re.search(pattern, cleaned)
            if match:
                entities = {
                    key: value.strip()
                    for key, value in match.groupdict().items()
                    if value
                }
                return {"intent": intent_name, "entities": entities}

    # No built-in intent matched — commands.py will check custom commands
    # before finally falling back to "unknown".
    return {"intent": "unknown", "entities": {"raw_text": cleaned}}
