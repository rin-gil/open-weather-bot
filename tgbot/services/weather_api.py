""" Classes for getting weather information """

from aiohttp import ClientSession

from tgbot.config import load_config, BOT_LOGO
from tgbot.misc.logging import logger
from tgbot.models.database import database, UserWeatherSettings
from tgbot.models.localization import locale
from tgbot.services.weather_formatter import CityData, formatter


class WeatherAPI:
    """ A class for working with the OpenWeatherMap API """
    _GEOCODING_API_URL: str = 'https://api.openweathermap.org/geo/1.0'
    _CURRENT_WEATHER_API_URL: str = 'https://api.openweathermap.org/data/2.5/weather'
    _WEATHER_FORECAST_API_URL: str = 'https://api.openweathermap.org/data/2.5/forecast'

    def __init__(self, token: str) -> None:
        """
        Gets OpenWeatherAPI token

        :param token: OpenWeatherAPI token
        """
        self._API_KEY = token

    @staticmethod
    async def _correct_user_input(string: str) -> str:
        """
        Removes everything from the string except letters, spaces and hyphens

        :param string: source string
        :return: processed string
        """
        processed_string: str = ''
        for char in string[:72]:
            if char.isalpha() or char == '-':
                processed_string += char
            elif char.isspace() and (not processed_string or not processed_string[-1].isspace()):
                processed_string += char
        return processed_string

    async def get_cities(self,
                         lang: str,
                         city_name: [str | None] = None,
                         latitude: [float | None] = None,
                         longitude: [float | None] = None) -> list[CityData]:
        """
        Returns the list of found cities

        :param lang: user language code
        :param city_name: city name
        :param latitude: city latitude
        :param longitude: city longitude
        :return: list of found cities
        """
        if city_name is None:
            api_url: str = f'{self._GEOCODING_API_URL}/reverse' \
                           f'?lat={latitude}&lon={longitude}' \
                           f'&limit=5&appid={self._API_KEY}'
        else:
            api_url: str = f'{self._GEOCODING_API_URL}/direct' \
                           f'?q={await self._correct_user_input(string=city_name)}' \
                           f'&limit=5&appid={self._API_KEY}'
        async with ClientSession() as session:
            async with session.get(url=api_url) as responce:
                await database.increase_api_counter()
                result: list[CityData] = []
                if responce.status == 200:
                    cities: list[dict] = await responce.json()
                    if len(cities) != 0:
                        [result.append(await formatter.city_data(data=city, lang=lang)) for city in cities]
                else:
                    error: dict = await responce.json()
                    logger.error('Error when requesting WeatherGeocodeAPI: %s', error.get('message'))
                return result

    async def get_current_weather(self, user_id: int) -> str:
        """
        Gets current weather data from the OpenWeatherMap service and outputs them in formatted form

        :param user_id: user id
        :return: formatted current weather data
        """
        settings: UserWeatherSettings = await database.get_user_settings(user_id=user_id)
        async with ClientSession() as session:
            async with session.get(url=f'{self._CURRENT_WEATHER_API_URL}'
                                       f'?lat={settings.latitude}'
                                       f'&lon={settings.longitude}'
                                       f'&lang={settings.lang}'
                                       f'&units={settings.units}'
                                       f'&appid={self._API_KEY}') as responce:
                await database.increase_api_counter()
                if responce.status == 200:
                    current_weather: dict = await responce.json()
                    return await formatter.current_weather(data=current_weather, units=settings.units,
                                                           city=settings.city, lang=settings.lang)
                else:
                    error: dict = await responce.json()
                    logger.error('Error when requesting CurrentWeatherAPI: %s', error.get('message'))
                    return await locale.get_translate(lang=settings.lang, translate='error_weather')

    async def get_weather_forecast(self, user_id: int) -> str:
        """
        Returns the image with the weather forecast for 24 hours, in case of error - the bot logo

        :param user_id: user id
        :return: Path to the image file
        """
        settings: UserWeatherSettings = await database.get_user_settings(user_id=user_id)
        async with ClientSession() as session:
            async with session.get(url=f'{self._WEATHER_FORECAST_API_URL}'
                                       f'?lat={settings.latitude}'
                                       f'&lon={settings.longitude}'
                                       f'&lang={settings.lang}'
                                       f'&units={settings.units}'
                                       f'&cnt=8'
                                       f'&appid={self._API_KEY}') as responce:
                await database.increase_api_counter()
                if responce.status == 200:
                    weather_forecast: dict = await responce.json()
                    return await formatter.weather_forecast(data=weather_forecast.get('list'), units=settings.units,
                                                            user_id=user_id)
                else:
                    error: dict = await responce.json()
                    logger.error('Error when requesting WeatherForecastAPI: %s', error.get('message'))
                    return BOT_LOGO


weather: WeatherAPI = WeatherAPI(token=load_config().weather_api.token)
