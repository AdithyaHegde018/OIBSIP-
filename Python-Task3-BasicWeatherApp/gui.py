import tkinter as tk
from tkinter import messagebox

from weather_api import (
    get_current_weather,
    get_hourly_forecast,
    get_daily_forecast,
    get_icon_url,
    WeatherAPIError,
)
from utils import format_temp, load_icon_image, date_to_weekday
from location import get_city_from_ip, LocationError


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather App")
        self.root.geometry("420x760")
        self.root.resizable(False, False)

        self.unit = "metric"  # "metric" = Celsius, "imperial" = Fahrenheit
        self.last_city = ""

        self._build_header()
        self._build_search_area()
        self._build_current_weather_area()
        self._build_hourly_forecast_area()
        self._build_daily_forecast_area()
        self._build_status_area()

    # ---------- UI SECTIONS ----------

    def _build_header(self):
        header = tk.Label(
            self.root, text="Advanced Weather App",
            font=("Segoe UI", 16, "bold")
        )
        header.pack(pady=(15, 10))

    def _build_search_area(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="City:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
        self.city_entry = tk.Entry(frame, width=25, font=("Segoe UI", 10))
        self.city_entry.grid(row=0, column=1, padx=5)
        self.city_entry.bind("<Return>", lambda event: self.search_weather())

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=8)

        search_btn = tk.Button(button_frame, text="Search Weather", command=self.search_weather)
        search_btn.grid(row=0, column=0, padx=5)

        location_btn = tk.Button(button_frame, text="Use My Location", command=self.use_my_location)
        location_btn.grid(row=0, column=1, padx=5)

        unit_frame = tk.Frame(self.root)
        unit_frame.pack(pady=(0, 5))

        self.unit_var = tk.StringVar(value="metric")
        tk.Radiobutton(
            unit_frame, text="Celsius", variable=self.unit_var, value="metric",
            command=self.on_unit_change
        ).grid(row=0, column=0, padx=5)
        tk.Radiobutton(
            unit_frame, text="Fahrenheit", variable=self.unit_var, value="imperial",
            command=self.on_unit_change
        ).grid(row=0, column=1, padx=5)

    def _build_current_weather_area(self):
        self.weather_frame = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=1)
        self.weather_frame.pack(pady=10, padx=15, fill="x")

        self.location_label = tk.Label(self.weather_frame, text="", font=("Segoe UI", 13, "bold"))
        self.location_label.pack(pady=(10, 0))

        self.icon_label = tk.Label(self.weather_frame)
        self.icon_label.pack()

        self.temp_label = tk.Label(self.weather_frame, text="", font=("Segoe UI", 22))
        self.temp_label.pack()

        self.feels_like_label = tk.Label(self.weather_frame, text="", font=("Segoe UI", 10))
        self.feels_like_label.pack()

        self.description_label = tk.Label(self.weather_frame, text="", font=("Segoe UI", 11, "italic"))
        self.description_label.pack(pady=(0, 5))

        details_frame = tk.Frame(self.weather_frame)
        details_frame.pack(pady=(5, 10))

        self.humidity_label = tk.Label(details_frame, text="", font=("Segoe UI", 9))
        self.humidity_label.grid(row=0, column=0, padx=10)

        self.wind_label = tk.Label(details_frame, text="", font=("Segoe UI", 9))
        self.wind_label.grid(row=0, column=1, padx=10)

        self.pressure_label = tk.Label(details_frame, text="", font=("Segoe UI", 9))
        self.pressure_label.grid(row=0, column=2, padx=10)

    def _build_hourly_forecast_area(self):
        tk.Label(self.root, text="Next Few Hours", font=("Segoe UI", 11, "bold")).pack(pady=(5, 2))

        self.hourly_frame = tk.Frame(self.root)
        self.hourly_frame.pack(pady=(0, 5))

        # Pre-create 6 slot frames so we can just update them each search
        self.hourly_slots = []
        for i in range(6):
            slot = tk.Frame(self.hourly_frame, relief=tk.RIDGE, borderwidth=1, padx=6, pady=4)
            slot.grid(row=0, column=i, padx=3)

            time_label = tk.Label(slot, text="--:--", font=("Segoe UI", 8, "bold"))
            time_label.pack()

            icon_label = tk.Label(slot)
            icon_label.pack()

            temp_label = tk.Label(slot, text="--°", font=("Segoe UI", 9))
            temp_label.pack()

            self.hourly_slots.append({
                "time": time_label,
                "icon": icon_label,
                "temp": temp_label,
            })

    def _build_daily_forecast_area(self):
        tk.Label(self.root, text="5-Day Forecast", font=("Segoe UI", 11, "bold")).pack(pady=(5, 2))

        self.daily_frame = tk.Frame(self.root)
        self.daily_frame.pack(pady=(0, 5))

        self.daily_slots = []
        for i in range(5):
            slot = tk.Frame(self.daily_frame, relief=tk.RIDGE, borderwidth=1, padx=6, pady=4)
            slot.grid(row=0, column=i, padx=3)

            day_label = tk.Label(slot, text="---", font=("Segoe UI", 8, "bold"))
            day_label.pack()

            icon_label = tk.Label(slot)
            icon_label.pack()

            high_low_label = tk.Label(slot, text="--° / --°", font=("Segoe UI", 8))
            high_low_label.pack()

            self.daily_slots.append({
                "day": day_label,
                "icon": icon_label,
                "high_low": high_low_label,
            })

    def _build_status_area(self):
        self.status_label = tk.Label(self.root, text="", fg="red", font=("Segoe UI", 9), wraplength=380)
        self.status_label.pack(pady=(5, 10))

    # ---------- LOGIC ----------

    def set_status(self, message, is_error=True):
        self.status_label.config(text=message, fg="red" if is_error else "green")

    def clear_weather_display(self):
        self.location_label.config(text="")
        self.icon_label.config(image="")
        self.icon_label.image = None
        self.temp_label.config(text="")
        self.feels_like_label.config(text="")
        self.description_label.config(text="")
        self.humidity_label.config(text="")
        self.wind_label.config(text="")
        self.pressure_label.config(text="")

        for slot in self.hourly_slots:
            slot["time"].config(text="--:--")
            slot["icon"].config(image="")
            slot["icon"].image = None
            slot["temp"].config(text="--°")

        for slot in self.daily_slots:
            slot["day"].config(text="---")
            slot["icon"].config(image="")
            slot["icon"].image = None
            slot["high_low"].config(text="--° / --°")

    def search_weather(self):
        city = self.city_entry.get()
        self.set_status("")  # clear old status

        try:
            data = get_current_weather(city, units=self.unit)
            hourly = get_hourly_forecast(city, units=self.unit)
            daily = get_daily_forecast(city, units=self.unit)
        except WeatherAPIError as e:
            self.clear_weather_display()
            self.set_status(e.message)
            return
        except Exception:
            self.clear_weather_display()
            self.set_status("An unexpected error occurred. Please try again.")
            return

        self._display_weather(data)
        self._display_hourly(hourly)
        self._display_daily(daily)
        self.last_city = data["city"]
        self.set_status(f"Weather updated for {data['city']}.", is_error=False)

    def _display_weather(self, data):
        unit_symbol = "°C" if self.unit == "metric" else "°F"
        speed_unit = "m/s" if self.unit == "metric" else "mph"

        location_text = data["city"]
        if data["country"]:
            location_text += f", {data['country']}"
        self.location_label.config(text=location_text)

        self.temp_label.config(text=format_temp(data["temp"], unit_symbol))
        self.feels_like_label.config(text=f"Feels like: {format_temp(data['feels_like'], unit_symbol)}")
        self.description_label.config(text=data["description"])

        self.humidity_label.config(text=f"Humidity: {data['humidity']}%")
        self.wind_label.config(text=f"Wind: {data['wind_speed']} {speed_unit}")
        self.pressure_label.config(text=f"Pressure: {data['pressure']} hPa")

        icon_url = get_icon_url(data["icon_code"])
        icon_image = load_icon_image(icon_url)
        if icon_image:
            self.icon_label.config(image=icon_image)
            self.icon_label.image = icon_image  # keep a reference so it isn't garbage-collected
        else:
            self.icon_label.config(image="")
            self.icon_label.image = None

    def _display_hourly(self, hourly_data):
        unit_symbol = "°C" if self.unit == "metric" else "°F"

        for i, slot in enumerate(self.hourly_slots):
            if i < len(hourly_data):
                entry = hourly_data[i]
                slot["time"].config(text=entry["time"])
                slot["temp"].config(text=format_temp(entry["temp"], unit_symbol))

                icon_url = get_icon_url(entry["icon_code"], size="1x")
                icon_image = load_icon_image(icon_url, size=(35, 35))
                if icon_image:
                    slot["icon"].config(image=icon_image)
                    slot["icon"].image = icon_image
                else:
                    slot["icon"].config(image="")
                    slot["icon"].image = None
            else:
                slot["time"].config(text="--:--")
                slot["icon"].config(image="")
                slot["icon"].image = None
                slot["temp"].config(text="--°")

    def _display_daily(self, daily_data):
        unit_symbol = "°C" if self.unit == "metric" else "°F"

        for i, slot in enumerate(self.daily_slots):
            if i < len(daily_data):
                entry = daily_data[i]
                slot["day"].config(text=date_to_weekday(entry["date"]))
                slot["high_low"].config(
                    text=f"{format_temp(entry['high'], unit_symbol)} / {format_temp(entry['low'], unit_symbol)}"
                )

                icon_url = get_icon_url(entry["icon_code"], size="1x")
                icon_image = load_icon_image(icon_url, size=(35, 35))
                if icon_image:
                    slot["icon"].config(image=icon_image)
                    slot["icon"].image = icon_image
                else:
                    slot["icon"].config(image="")
                    slot["icon"].image = None
            else:
                slot["day"].config(text="---")
                slot["icon"].config(image="")
                slot["icon"].image = None
                slot["high_low"].config(text="--° / --°")

    def on_unit_change(self):
        self.unit = self.unit_var.get()

        # Re-fetch using the last searched city, if there is one.
        # We re-fetch rather than converting locally because it keeps the
        # code simple and guarantees hourly/daily data is refreshed too —
        # but we only do this on unit toggle, never during typing, so
        # it stays a single deliberate API call per toggle.
        if self.last_city.strip():
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, self.last_city)
            self.search_weather()

    def use_my_location(self):
        self.set_status("Detecting your location...", is_error=False)
        self.root.update_idletasks()  # show the message immediately before the network call

        try:
            city = get_city_from_ip()
        except LocationError as e:
            self.set_status(e.message)
            return

        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, city)
        self.search_weather()


def run_app():
    root = tk.Tk()
    app = WeatherApp(root)

    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    run_app()
