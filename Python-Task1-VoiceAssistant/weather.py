"""
weather.py
-----------
OpenWeatherMap integration.

Handles every failure mode explicitly:
    * missing/invalid API key
    * invalid city name
    * network failure
    * request timeout
    * malformed/unexpected API response

Never raises out of get_weather() — always returns a plain-language
string that is safe to speak directly to the user.
"""

import requests

from config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, WEATHER_ENABLED

REQUEST_TIMEOUT_SECONDS = 6


def get_weather(city: str) -> str:
    """
    Fetch current weather for `city` and return a human-readable summary.
    """
    if not WEATHER_ENABLED:
        return ("Weather lookups are not configured. Please add an "
                "OPENWEATHER_API_KEY to your .env file.")

    if not city or not city.strip():
        return "I didn't catch which city you want the weather for."

    params = {
        "q": city.strip(),
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # Celsius
    }

    try:
        response = requests.get(
            OPENWEATHER_BASE_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.exceptions.Timeout:
        return "The weather service took too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        return "I couldn't reach the weather service. Please check your internet connection."
    except requests.exceptions.RequestException as error:
        return f"Something went wrong while fetching the weather: {error}"

    if response.status_code in (401, 403):
        return "The weather API key seems to be invalid. Please check your .env file."
    if response.status_code == 404:
        return f"I couldn't find weather data for '{city}'. Please check the city name."
    if response.status_code != 200:
        return f"The weather service returned an unexpected error (status {response.status_code})."

    try:
        data = response.json()
        name = data["name"]
        main = data["main"]
        weather_desc = data["weather"][0]["description"]
        wind_speed = data.get("wind", {}).get("speed", "unknown")

        temp = main.get("temp")
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")

        summary = (
            f"The weather in {name} is {weather_desc} with a temperature of "
            f"{temp}°C"
        )
        if feels_like is not None:
            summary += f", feeling like {feels_like}°C"
        summary += f". Humidity is {humidity}% and wind speed is {wind_speed} meters per second."
        return summary
    except (KeyError, IndexError, ValueError):
        return "I received an unexpected response from the weather service."
