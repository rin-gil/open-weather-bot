"""Classes for working with data"""

from typing import NamedTuple


class User(NamedTuple):
    """A class that describes a user"""

    id: int
    dialog_id: int


class UserWeatherSettings(NamedTuple):
    """A class that describes the user's weather settings"""

    lang: str
    city: str
    latitude: float
    longitude: float
    units: str


class CityData(NamedTuple):
    """A class describing city data"""

    name: str
    full_name: str
    latitude: float
    longitude: float


class CurrentWeatherData(NamedTuple):
    """A class describing current weather data"""

    temp: int
    feels_like: int
    weather_code: int
    weather_description: str
    wind_speed: int
    gust: int | None
    humidity: int
    pressure: int
    visibility: float
    precipitation: float | None
    time: str
    sunrise: str
    sunset: str


class ForecastData(NamedTuple):
    """A class describing weather forecast data"""

    time: list[str]
    ico_code: list[str]
    temp: list[str]
    wind_speed: list[str]
