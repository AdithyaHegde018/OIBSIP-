import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

TIMEOUT = 10  # seconds


class WeatherAPIError(Exception):
    """Custom exception so the GUI can catch one clean error type."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _check_api_key():
    if not API_KEY:
        raise WeatherAPIError("OpenWeatherMap API key is missing. Please check your .env file.")


def _handle_response(response):
    """Shared response handling for both endpoints."""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise WeatherAPIError("OpenWeatherMap API key is missing or invalid.")
    elif response.status_code == 404:
        raise WeatherAPIError("City not found. Please check the city name.")
    else:
        raise WeatherAPIError("Weather service is currently unavailable.")


def _request(url, params):
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        return _handle_response(response)
    except requests.exceptions.Timeout:
        raise WeatherAPIError("The request timed out. Please check your internet connection.")
    except requests.exceptions.ConnectionError:
        raise WeatherAPIError("No internet connection available.")
    except WeatherAPIError:
        raise
    except Exception:
        raise WeatherAPIError("Something went wrong while contacting the weather service.")


def get_current_weather(city, units="metric"):
    """
    Returns a dict with current weather info for the given city.
    units: "metric" (Celsius) or "imperial" (Fahrenheit)
    """
    _check_api_key()
    if not city or not city.strip():
        raise WeatherAPIError("Please enter a city name.")

    params = {"q": city.strip(), "appid": API_KEY, "units": units}
    data = _request(CURRENT_URL, params)

    return {
        "city": data.get("name", ""),
        "country": data.get("sys", {}).get("country", ""),
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"],
        "description": data["weather"][0]["description"].title(),
        "icon_code": data["weather"][0]["icon"],
        "main_condition": data["weather"][0]["main"],
    }


def get_forecast_raw(city, units="metric"):
    """
    Returns the raw 3-hour interval forecast list (up to 5 days) for a city.
    Used internally by both hourly and daily forecast functions.
    """
    _check_api_key()
    if not city or not city.strip():
        raise WeatherAPIError("Please enter a city name.")

    params = {"q": city.strip(), "appid": API_KEY, "units": units}
    data = _request(FORECAST_URL, params)
    return data.get("list", [])


def get_hourly_forecast(city, units="metric", count=6):
    """
    Returns the next `count` forecast entries (3-hour steps from the API),
    each as a dict with time, temp, description, icon_code.

    Note: OpenWeatherMap's free forecast API gives data in 3-hour steps,
    not true 1-hour steps — so "next 6 hours" here means the next 6
    forecast entries (roughly the next 18 hours) so the forecast panel
    has enough to show.
    """
    raw = get_forecast_raw(city, units)
    hourly = []
    for entry in raw[:count]:
        hourly.append({
            "time": entry["dt_txt"].split(" ")[1][:5],  # "HH:MM"
            "temp": entry["main"]["temp"],
            "description": entry["weather"][0]["description"].title(),
            "icon_code": entry["weather"][0]["icon"],
            "main_condition": entry["weather"][0]["main"],
        })
    return hourly


def get_daily_forecast(city, units="metric"):
    """
    Returns a list of up to 5 daily summaries (date, high, low, description, icon)
    built by grouping the 3-hour forecast entries by calendar date.
    """
    raw = get_forecast_raw(city, units)
    days = {}

    for entry in raw:
        date_str = entry["dt_txt"].split(" ")[0]  # "YYYY-MM-DD"
        temp = entry["main"]["temp"]
        if date_str not in days:
            days[date_str] = {
                "date": date_str,
                "high": temp,
                "low": temp,
                "description": entry["weather"][0]["description"].title(),
                "icon_code": entry["weather"][0]["icon"],
                "main_condition": entry["weather"][0]["main"],
            }
        else:
            days[date_str]["high"] = max(days[date_str]["high"], temp)
            days[date_str]["low"] = min(days[date_str]["low"], temp)

    return list(days.values())[:5]


def get_icon_url(icon_code, size="2x"):
    """Builds the URL for a weather icon image."""
    return f"https://openweathermap.org/img/wn/{icon_code}@{size}.png"


if __name__ == "__main__":
    # Quick manual test — run this file directly to sanity-check the module
    try:
        current = get_current_weather("Mangalore")
        print("CURRENT:", current)

        hourly = get_hourly_forecast("Mangalore")
        print("\nHOURLY:")
        for h in hourly:
            print(" ", h)

        daily = get_daily_forecast("Mangalore")
        print("\nDAILY:")
        for d in daily:
            print(" ", d)

    except WeatherAPIError as e:
        print("ERROR:", e.message)
