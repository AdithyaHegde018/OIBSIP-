"""
database.py
-------------
All SQLite access for the BMI Calculator lives here. This is the ONLY
module that imports sqlite3 -- gui.py never talks to the database
directly, it only calls the functions below.

Database file: bmi_calculator.db (created automatically on first use,
in the same folder as this file).

Table: bmi_records
    id           INTEGER PRIMARY KEY AUTOINCREMENT
    user_name    TEXT
    weight       REAL
    height       REAL
    bmi          REAL
    category     TEXT
    recorded_at  TEXT   (ISO-formatted date/time string)
"""

import os
import sqlite3
from datetime import datetime

DB_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmi_calculator.db")


def _get_connection() -> sqlite3.Connection:
    """Open a connection to the database file (created automatically if missing)."""
    return sqlite3.connect(DB_FILENAME)


def create_database() -> bool:
    """
    Create the bmi_records table if it doesn't already exist.

    Safe to call every time the app starts -- CREATE TABLE IF NOT EXISTS
    means it's a no-op on every run after the first.

    Returns True on success, False if something went wrong (e.g. the
    folder isn't writable).
    """
    try:
        connection = _get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
        connection.close()
        return True
    except sqlite3.Error as error:
        print(f"[database] Could not create database: {error}")
        return False


def save_record(user_name: str, weight: float, height: float, bmi: float, category: str) -> tuple[bool, str | None]:
    """
    Insert one BMI record. Returns (success, error_message).

    The timestamp is generated here (not passed in) so every caller
    gets a consistent, correctly-formatted "recorded at" time.
    """
    recorded_at = datetime.now().strftime("%d-%m-%Y %H:%M")

    try:
        connection = _get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO bmi_records (user_name, weight, height, bmi, category, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_name, weight, height, bmi, category, recorded_at),
        )
        connection.commit()
        connection.close()
        return True, None
    except sqlite3.Error as error:
        return False, f"Could not save the record: {error}"


def get_user_records(user_name: str) -> list[dict]:
    """
    Fetch all records for one user, oldest first (good for chart trends).

    Returns a list of dicts, e.g.:
        [{"id": 1, "user_name": "Adithya", "weight": 65.0, "height": 170.0,
          "bmi": 22.49, "category": "Normal", "recorded_at": "05-09-2026 10:30"}, ...]

    Returns an empty list if there are no records or if a database error
    occurs -- callers don't need a separate error path for "no data".
    """
    try:
        connection = _get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM bmi_records WHERE user_name = ? ORDER BY id ASC",
            (user_name,),
        )
        rows = cursor.fetchall()
        connection.close()
        return [dict(row) for row in rows]
    except sqlite3.Error as error:
        print(f"[database] Could not fetch records for {user_name}: {error}")
        return []


def get_all_records() -> list[dict]:
    """Fetch every record for every user, most recent first."""
    try:
        connection = _get_connection()
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bmi_records ORDER BY id DESC")
        rows = cursor.fetchall()
        connection.close()
        return [dict(row) for row in rows]
    except sqlite3.Error as error:
        print(f"[database] Could not fetch records: {error}")
        return []


def get_all_user_names() -> list[str]:
    """
    Return a sorted list of distinct user names that have at least one
    saved record. Used to populate the user-selection dropdown in the
    History window (Phase 8) and Chart window (Phase 9).
    """
    try:
        connection = _get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT user_name FROM bmi_records ORDER BY user_name COLLATE NOCASE")
        names = [row[0] for row in cursor.fetchall()]
        connection.close()
        return names
    except sqlite3.Error as error:
        print(f"[database] Could not fetch user names: {error}")
        return []
