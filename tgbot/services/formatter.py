"""Formats weather data into the required view"""

from math import log

from tgbot.middlewares.localization import i18n
from tgbot.services.classes import CurrentWeatherData


_ = i18n.gettext  # Alias for gettext method


class FormatWeather:
    """A class for formatting weather data"""

    @staticmethod
    async def correct_user_input(city_name: str) -> str:
        """Removes everything from the city_name except letters, spaces and hyphens"""
        processed_string: str = ""
        # cut city_name to 72, because this is max length of the city name
        for char in city_name[:72]:
            if char.isalpha() or char == "-":
                processed_string += char
            elif char.isspace() and (not processed_string or not processed_string[-1].isspace()):
                processed_string += char
        return processed_string

    @staticmethod
    async def _get_weather_emoji(weather: int) -> str:
        """Returns emoji by weather code from OpenWeatherMap"""
        if weather in (800,):  # clear
            weather_emoji: str = "☀"
        elif weather in (801,):  # light clouds
            weather_emoji = "🌤"
        elif weather in (803, 804):  # clouds
            weather_emoji = "🌥"
        elif weather in (802,):  # scattered clouds
            weather_emoji = "☁"
        elif weather in (500, 501, 502, 503, 504):  # rain
            weather_emoji = "🌦"
        elif weather in (300, 301, 302, 310, 311, 312, 313, 314, 321, 520, 521, 522, 531):  # drizzle
            weather_emoji = "🌧"
        elif weather in (200, 201, 202, 210, 211, 212, 221, 230, 231, 232):  # thunderstorm
            weather_emoji = "⛈"
        elif weather in (511, 600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622):  # snow
            weather_emoji = "🌨"
        elif weather in (701, 711, 721, 731, 741, 751, 761, 762, 771, 781):  # atmosphere
            weather_emoji = "🌫"
        else:  # default
            weather_emoji = "🌀"
        return weather_emoji

    @staticmethod
    async def _calculate_dew_point(temp: int, humidity: int) -> int:
        """Calculates the surface temperature at which condensation occurs (dew point)"""
        const_a: float = 17.27
        const_b: float = 237.7

        def func():  # type: ignore
            return (const_a * temp) / (const_b + temp) + log(humidity / 100)

        return round((const_b * func()) / (const_a - func()))  # type: ignore

    async def format_current_weather(
        self, weather_data: CurrentWeatherData, units: str, city: str, lang_code: str
    ) -> str:
        """Returns the current weather data in the desired form"""
        emoji = await self._get_weather_emoji(weather=weather_data.weather_code)
        temp_units: str = "°C" if units == "metric" else "°F"
        wind_units: str = "m/s" if units == "metric" else "mph"
        dew_point: int = await self._calculate_dew_point(temp=weather_data.temp, humidity=weather_data.humidity)

        if weather_data.precipitation:
            precipitation: str = (
                f", <b>{weather_data.precipitation} mm </b>" + _("of precipitation in one hour", locale=lang_code) + ""
            )
        else:
            precipitation = ""
        if weather_data.gust:
            wind_gust: str = ", " + _("gusts to", locale=lang_code) + f": <b>{weather_data.gust} {wind_units}</b>"
        else:
            wind_gust = ""
        current_weather: str = (
            f"<b>{city}, {weather_data.time}</b>\n"
            + f"{emoji} {weather_data.weather_description}{precipitation}\n\n"
            + f"🌡 <b>{weather_data.temp}{temp_units}</b>, "
            + _("feels like", locale=lang_code)
            + f" <b>{weather_data.feels_like}{temp_units}</b>\n\n"
            + "💦 "
            + _("Humidity", locale=lang_code)
            + f": <b>{weather_data.humidity}%</b>, "
            + _("Dew point", locale=lang_code)
            + f": <b>{dew_point}{temp_units}</b>\n"
            + "💨 "
            + _("Wind speed", locale=lang_code)
            + f": <b>{weather_data.wind_speed} {wind_units}</b>{wind_gust}\n"
            + "🌡 "
            + _("Pressure", locale=lang_code)
            + f": <b>{weather_data.pressure} hPa</b>\n"
            + "🌫️ "
            + _("Visibility", locale=lang_code)
            + f": <b>{weather_data.visibility} km</b>\n\n"
            + "🌅 "
            + _("Sunrise", locale=lang_code)
            + f": <b>{weather_data.sunrise}</b>  🌇 "
            + _("Sunset", locale=lang_code)
            + f": <b>{weather_data.sunset}</b>"
        )
        return current_weather
