# Advanced Weather App

## Overview

A desktop weather application built with Python and Tkinter as part of the **Oasis Infobyte Python Programming Internship (Task 4 – Advanced Level)**. It fetches live weather data from the OpenWeatherMap API and displays current conditions, an hourly forecast, and a 5-day forecast, with support for Celsius/Fahrenheit and optional IP-based location detection.

## Features

- Search weather by city name
- Current temperature, feels-like temperature, humidity, wind speed, and pressure
- Weather condition description and icon
- Next-few-hours forecast (from OpenWeatherMap's 3-hour interval data)
- 5-day forecast with daily high/low temperatures
- Celsius / Fahrenheit toggle
- Optional "Use My Location" button (IP-based, city-level accuracy)
- Graceful in-GUI error handling — invalid cities, missing/invalid API keys, no internet, timeouts, and failed icon downloads never crash the app

## Technologies Used

- Python 3.10+
- Tkinter (GUI)
- `requests` (HTTP calls to OpenWeatherMap and IP geolocation)
- `python-dotenv` (secure API key loading)
- `Pillow` (weather icon rendering)
- OpenWeatherMap API (current weather + forecast)
- ip-api.com (optional IP-based location detection)

## Project Structure

```
Python-Task4-BasicWeatherApp/
├── main.py            # Application entry point
├── gui.py             # Tkinter interface and event handling
├── weather_api.py     # OpenWeatherMap API requests and data processing
├── location.py        # Optional IP-based location detection
├── utils.py           # Temperature conversion, formatting, icon loading
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── screenshots/
```

## Installation

```powershell
git clone <your-repo-url>
cd OIBSIP/Python-Task4-BasicWeatherApp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## API Key Setup

1. Create a free account at [OpenWeatherMap](https://openweathermap.org/api).
2. Generate an API key from your account dashboard.
3. Copy `.env.example` to a new file named `.env`.
4. Add your key:
   ```
   OPENWEATHER_API_KEY=your_actual_key_here
   ```
5. New API keys can take up to a couple of hours to activate.

## How to Run

```powershell
python main.py
```

## How the Application Works

1. The user enters a city name (or uses "Use My Location" for an IP-based guess).
2. `weather_api.py` calls OpenWeatherMap's current weather and forecast endpoints.
3. The forecast endpoint returns data in 3-hour steps; `weather_api.py` slices this into an "upcoming hours" view and groups it by date for the 5-day view.
4. `gui.py` renders all of this in a Tkinter window, and re-fetches automatically whenever the temperature unit is toggled.

## Screenshots

![Main Weather](screenshots/main-weather.png)
![Hourly Forecast](screenshots/hourly-forecast.png)
![Five Day Forecast](screenshots/five-day-forecast.png)
![Fahrenheit Mode](screenshots/fahrenheit-mode.png)
![Error Handling](screenshots/error-handling.png)

## Error Handling

The app handles the following without crashing, showing a friendly message in the GUI instead:
- Empty or whitespace-only city input
- City not found
- Missing or invalid API key
- No internet connection / request timeout
- Failed weather icon downloads
- Failed location detection

## Security

- The API key is loaded from a `.env` file via `python-dotenv` and is never hard-coded.
- `.env` is excluded from version control via `.gitignore`; only `.env.example` (with a placeholder) is committed.
- Location detection is IP-based only (approximate, city-level) — no GPS or precise personal location data is collected or stored.

## Known Limitations

- OpenWeatherMap's free tier provides forecast data in 3-hour steps, so the "upcoming hours" view shows the next 6 forecast entries (~18 hours) rather than literal hour-by-hour data.
- Changing the API key in `.env` requires restarting the app to take effect.
- IP-based location detection gives an approximate city, which can occasionally be inaccurate depending on network/ISP.

## Future Improvements

- Add a search history / favorite cities list
- Add a settings panel to persist unit preference between sessions
- Add unit tests for `weather_api.py` and `utils.py`
- Support switching to a paid OpenWeatherMap tier for true hourly data

## Demo Video

[Link to demo video]

## Author

Adithya Hegde
