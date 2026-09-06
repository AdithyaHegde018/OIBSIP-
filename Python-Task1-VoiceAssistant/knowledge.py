"""
knowledge.py
-------------
General knowledge Q&A.

Strategy:
    1. Check a small local knowledge base first (fast, offline, no API
       dependency for common questions).
    2. Fall back to the DuckDuckGo Instant Answer API (no API key needed)
       for anything else.
    3. If neither has an answer, say so honestly instead of inventing one.
"""

import requests

from config import KNOWLEDGE_API_URL

REQUEST_TIMEOUT_SECONDS = 6

_LOCAL_KNOWLEDGE_BASE = {
    "your name": "I'm your Python voice assistant, built for the Oasis Infobyte internship.",
    "who made you": "I was built as part of the Oasis Infobyte Python Programming Internship.",
    "who created you": "I was built as part of the Oasis Infobyte Python Programming Internship.",
    "capital of india": "The capital of India is New Delhi.",
    "capital of france": "The capital of France is Paris.",
}


def _check_local_knowledge_base(question: str) -> str | None:
    question = question.lower().strip().rstrip("?")
    for key, answer in _LOCAL_KNOWLEDGE_BASE.items():
        if key in question:
            return answer
    return None


def _query_duckduckgo(question: str) -> str | None:
    """Query DuckDuckGo's Instant Answer API. Returns None if no clear answer."""
    params = {
        "q": question,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }
    try:
        response = requests.get(
            KNOWLEDGE_API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None

    for field in ("AbstractText", "Answer"):
        value = data.get(field)
        if value:
            return value

    related = data.get("RelatedTopics") or []
    if related and isinstance(related[0], dict) and related[0].get("Text"):
        return related[0]["Text"]

    return None


def answer_question(question: str) -> str:
    """
    Answer a general-knowledge question, or admit uncertainty rather than
    inventing a fact.
    """
    if not question or not question.strip():
        return "I didn't catch the question."

    local_answer = _check_local_knowledge_base(question)
    if local_answer:
        return local_answer

    api_answer = _query_duckduckgo(question)
    if api_answer:
        return api_answer

    return "I'm not sure about that one — I don't want to guess and give you wrong information."
