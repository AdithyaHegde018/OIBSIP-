import io
from datetime import datetime

import requests
from PIL import Image, ImageTk


def format_temp(value, unit_symbol="°C"):
    """Format a temperature value to 1 decimal place with a unit symbol."""
    try:
        return f"{value:.1f}{unit_symbol}"
    except (TypeError, ValueError):
        return f"--{unit_symbol}"


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


def load_icon_image(icon_url, size=(80, 80)):
    """
    Downloads a weather icon and returns a Tkinter-compatible image.
    Returns None if anything goes wrong (no crash).
    """
    try:
        response = requests.get(icon_url, timeout=5)
        if response.status_code != 200:
            return None
        image_data = Image.open(io.BytesIO(response.content))
        image_data = image_data.resize(size)
        return ImageTk.PhotoImage(image_data)
    except Exception:
        return None


def date_to_weekday(date_str):
    """Converts 'YYYY-MM-DD' into a short weekday name like 'Mon'."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%a")
    except (ValueError, TypeError):
        return "--"
