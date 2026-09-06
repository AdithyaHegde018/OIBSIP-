"""
email_service.py
------------------
Voice-controlled email sending via smtplib.

Credentials are NEVER hard-coded — they come exclusively from environment
variables (see config.py / .env.example). If they're missing, the feature
is cleanly disabled rather than crashing the app.

The interactive flow (ask recipient -> subject -> message -> confirm ->
send) lives in run_email_flow(), which takes the same `listen`/`speak`
callables main.py already uses, so this module has no direct dependency
on voice_input/speech_output (easier to test in isolation).
"""

import re
import smtplib
from email.message import EmailMessage

from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT, EMAIL_ENABLED

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def send_email(to_address: str, subject: str, body: str) -> str:
    """
    Send an email and return a human-readable result message.
    Never raises — all smtplib/network errors are caught and translated.
    """
    if not EMAIL_ENABLED:
        return ("Email is not configured. Please set EMAIL_ADDRESS and "
                "EMAIL_PASSWORD in your .env file.")

    if not to_address or not _EMAIL_PATTERN.match(to_address.strip()):
        return f"'{to_address}' doesn't look like a valid email address."

    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = to_address.strip()
    message["Subject"] = subject or "(No subject)"
    message.set_content(body or "")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)
        return f"Email sent to {to_address}."
    except smtplib.SMTPAuthenticationError:
        return ("Email authentication failed. Please check your EMAIL_ADDRESS "
                "and EMAIL_PASSWORD (use an app password, not your normal login password).")
    except smtplib.SMTPConnectError:
        return "Could not connect to the email server. Please check your internet connection."
    except smtplib.SMTPException as error:
        return f"Failed to send email: {error}"
    except OSError as error:
        return f"A network error occurred while sending the email: {error}"


def run_email_flow(listen_fn, speak_fn) -> str:
    """
    Interactive voice-driven flow for composing and sending an email.

    `listen_fn` — a zero-arg callable returning recognized text (or None).
    `speak_fn`  — a callable(text) that speaks/prints a prompt.

    Returns the final status message (also spoken by the caller if desired).
    """
    if not EMAIL_ENABLED:
        return ("Email is not configured. Please set EMAIL_ADDRESS and "
                "EMAIL_PASSWORD in your .env file.")

    def ask(prompt: str) -> str:
        speak_fn(prompt)
        for _ in range(2):  # allow one retry if unheard
            answer = listen_fn()
            if answer:
                return answer
            speak_fn("Sorry, I didn't catch that. Could you repeat it?")
        return ""

    recipient = ask("Who is the recipient? Please say the email address.")
    if not recipient:
        return "I couldn't get a recipient, cancelling the email."

    subject = ask("What should the subject be?")
    body = ask("What would you like the message to say?")

    speak_fn(
        f"Sending an email to {recipient} with subject '{subject}' "
        f"and message '{body}'. Say yes to confirm or no to cancel."
    )
    confirmation = listen_fn() or ""
    if "yes" not in confirmation:
        return "Email cancelled."

    speak_fn("Sending email...")
    return send_email(recipient, subject, body)
