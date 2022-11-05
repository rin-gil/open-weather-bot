""" Functions for getting weather information """

from aiohttp import ClientSession
from environs import Env

from tgbot.config import logger

env = Env()
env.read_env()
API_KEY: str = env.str('WEATHER_API')
GEOCODING_API_URL: str = 'https://api.openweathermap.org/geo/1.0/direct'


async def _correct_user_input(string: str) -> str:
    """
    Removes everything from the string except letters, spaces and hyphens

    :param string: source string
    :return: processed string
    """
    source_string: str = string[:30]
    processed_string: str = ''
    for char in source_string:
        if char.isalpha() or char == '-':
            processed_string += char
        elif char.isspace() and (not processed_string or not processed_string[-1].isspace()):
            processed_string += char
    return processed_string


async def _format_city_data(city: dict) -> dict:
    """
    Formats the city data

    :param city: city data
    :return: formatted city data
    """
    name: str = city.get('name')
    state: str = city.get('state')
    country: str = city.get('country')
    return dict(
        {
            'city_full_name': f'{name}, {state}, {country}' if state is not None else f'{name}, {country}',
            'lat': str(round(city.get('lat'), 6)),
            'lon': str(round(city.get('lon'), 6))
        }
    )


async def get_list_cities(city_name: str) -> list[dict]:
    """
    Returns the list of found cities

    :param city_name: city name
    :return: list of found cities
    """
    result: list[dict] = []
    async with ClientSession() as session:
        async with session.get(url=f'{GEOCODING_API_URL}'
                                   f'?q={await _correct_user_input(string=city_name)}'
                                   f'&limit=5'
                                   f'&appid={API_KEY}') as responce:
            if responce.status == 200:
                list_cities: list[dict] = await responce.json()
                if len(list_cities) != 0:
                    [result.append(await _format_city_data(city)) for city in list_cities]
            else:
                error: dict = await responce.json()
                logger.error('Error when requesting WeatherGeocodeAPI: %s', error.get('message'))
            return result


async def get_weather(user_id: int) -> str:
    # TODO сделать вывод информации о погоде
    return 'текущая погода'
