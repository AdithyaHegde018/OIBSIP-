import requests

IP_LOCATION_URL = "http://ip-api.com/json/"
TIMEOUT = 5


class LocationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_city_from_ip():
    """
    Attempts to detect the user's approximate city using IP-based geolocation.
    Returns the city name as a string, or raises LocationError on failure.

    Note: this is approximate (based on IP address, not GPS) and can be
    inaccurate, especially on mobile networks or behind a VPN.
    """
    try:
        response = requests.get(IP_LOCATION_URL, timeout=TIMEOUT)
        data = response.json()

        if data.get("status") != "success":
            raise LocationError("Could not detect your location automatically.")

        city = data.get("city")
        if not city:
            raise LocationError("Location detected, but no city name was available.")

        return city

    except requests.exceptions.Timeout:
        raise LocationError("Location lookup timed out. Please enter your city manually.")
    except requests.exceptions.ConnectionError:
        raise LocationError("No internet connection available for location lookup.")
    except LocationError:
        raise
    except Exception:
        raise LocationError("Something went wrong detecting your location.")


if __name__ == "__main__":
    try:
        print("Detected city:", get_city_from_ip())
    except LocationError as e:
        print("ERROR:", e.message)
