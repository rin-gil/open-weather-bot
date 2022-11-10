""" Formats the received weather data in the desired format """

from datetime import datetime
from typing import NamedTuple

from tgbot.models.localization import locale
from tgbot.services.draw_weather_image import ForecastData, weather_image


class CityData(NamedTuple):
    """ A class describing city data """
    full_name: str
    name: str
    latitude: float
    longitude: float


class WeatherFormat:
    """ A class for formatting weather data """

    @staticmethod
    async def _get_weather_emoji(weather: int) -> str:
        """
        Returns emoji by weather code from OpenWeatherMap

        :param weather: weather code
        :return: emoji
        """
        if weather in (800,):  # clear
            return '☀'
        if weather in (801,):  # light clouds
            return '🌤'
        if weather in (803, 804):  # clouds
            return '🌥'
        if weather in (802,):  # scattered clouds
            return '☁'
        if weather in (500, 501, 502, 503, 504):  # rain
            return '🌦'
        if weather in (300, 301, 302, 310, 311, 312, 313, 314, 321, 520, 521, 522, 531):  # drizzle
            return '🌧'
        if weather in (200, 201, 202, 210, 211, 212, 221, 230, 231, 232):  # thunderstorm
            return '⛈'
        if weather in (511, 600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622):  # snow
            return '🌨'
        if weather in (701, 711, 721, 731, 741, 751, 761, 762, 771, 781):  # atmosphere
            return '🌫'
        return '🌀'  # default

    @staticmethod
    async def city_data(data: dict, lang: str) -> CityData:
        """
        Formats the city data

        :param data: city data
        :param lang: user language code
        :return: formatted city data (object of CityData class)
        """
        name: str = data.get('name')
        state: str = data.get('state')
        country: str = data.get('country')
        local_names: [dict | None] = data.get('local_names')
        local_name: str = name if local_names is None else local_names.get(lang)
        city_name: str = name if local_name is None else local_name
        return CityData(
            full_name=f'{city_name}, {country}' if state is None else f'{city_name}, {state}, {country}',
            name=f'{city_name}',
            latitude=round(data.get('lat'), 6),
            longitude=round(data.get('lon'), 6)
        )

    async def current_weather(self, data: dict, units: str, city: str, lang: str) -> str:
        """
        Returns a string with formatted weather information

        :param data: dictionary with weather data
        :param units: temperature units
        :param city: city name
        :param lang: user language code
        :return: Formatted weather data
        """
        emoji: str = await self._get_weather_emoji(weather=data.get('weather')[0].get('id'))
        time: str = datetime.fromtimestamp(data.get('dt')).strftime('%d %b %H:%M')

        temp: int = round(data.get('main').get('temp'))
        temp_units: str = '°C' if units == 'metric' else '°F'
        feels_like: int = round(data.get('main').get('feels_like'))
        feels_like_locale: str = await locale.get_translate(lang=lang, translate='feels_like')
        description: str = data.get('weather')[0].get('description')

        humidity: int = data.get('main').get('humidity')
        humidity_locale: str = await locale.get_translate(lang=lang, translate='humidity')

        wind_speed: int = round(data.get('wind').get('speed'))
        wind_speed_locale: str = await locale.get_translate(lang=lang, translate='wind_speed')
        wind_units: str = 'm/s' if units == 'metric' else 'mph'
        gust: int = 0 if data.get('wind').get('gust') is None else round(data.get('wind').get('gust'))
        gust_locale: str = await locale.get_translate(lang=lang, translate='wind_gust')

        pressure: int = data.get('main').get('pressure')
        pressure_locale: str = await locale.get_translate(lang=lang, translate='pressure')

        visibility: float = round(data.get('visibility') / 1000, 1)
        visibility_locale: str = await locale.get_translate(lang=lang, translate='visibility')

        sunrise: str = datetime.fromtimestamp(data.get('sys').get('sunrise')).strftime('%H:%M')
        sunrise_locale: str = await locale.get_translate(lang=lang, translate='sunrise')
        sunset: str = datetime.fromtimestamp(data.get('sys').get('sunset')).strftime('%H:%M')
        sunset_locale: str = await locale.get_translate(lang=lang, translate='sunset')

        return f'<b>{emoji} {city}, {time}</b>\n' \
               f'\n' \
               f'🌡 <b>{temp} {temp_units}</b>, {feels_like_locale} <b>{feels_like} {temp_units}</b>, {description}\n' \
               f'\n' \
               f'💦 {humidity_locale}: <b>{humidity} %</b>\n' \
               f'💨 {wind_speed_locale}: <b>{wind_speed} {wind_units}</b>, {gust_locale} <b>{gust} {wind_units}</b>\n' \
               f'🌡 {pressure_locale}: <b>{pressure} hPa</b>\n' \
               f'🌫️ {visibility_locale}: <b>{visibility} km</b>\n' \
               f'\n' \
               f'🌅 {sunrise_locale}: <b>{sunrise}</b>, 🌇 {sunset_locale} <b>{sunset}</b>'

    @staticmethod
    async def weather_forecast(data: list[dict], units: str, user_id: int):
        """
        Formats the data for generating the weather forecast image

        :param data: weather data from the weather api request
        :param units: temperature units
        :param user_id: user id
        :return: the path to the file with the weather forecast image
        """
        time: list = []
        ico_code: list = []
        temp: list = []
        wind_speed: list = []
        for _ in data:
            time.append(datetime.fromtimestamp(_.get('dt')).strftime('%H:%M'))
            ico_code.append(_.get('weather')[0].get('icon'))
            temp.append(f'{round(_.get("main").get("temp"))}{"°C" if units == "metric" else "°F"}')
            wind_speed.append(f'{round(_.get("wind").get("speed"))} {"m/s" if units == "metric" else "mph"}')
        return await weather_image.draw_image(data=ForecastData(time=tuple(time), ico_code=tuple(ico_code),
                                                                temp=tuple(temp), wind_speed=tuple(wind_speed)),
                                              user_id=user_id)


formatter: WeatherFormat = WeatherFormat()
