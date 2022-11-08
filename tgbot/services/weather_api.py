""" Functions for getting weather information """

from aiohttp import ClientSession
from datetime import datetime

from tgbot.config import logger, load_config, BOT_LOGO, db
from tgbot.misc.locale import get_dialog_message_answer
from tgbot.models.database import UserWeatherSettings

from tgbot.services.generate_weather_forecast_image import format_weather_forecast_image

API_KEY: str = load_config().weather_api.token
GEOCODING_API_URL: str = 'https://api.openweathermap.org/geo/1.0/direct'
CURRENT_WEATHER_API_URL: str = 'https://api.openweathermap.org/data/2.5/weather'
WEATHER_FORECAST_API_URL: str = 'https://api.openweathermap.org/data/2.5/forecast'


async def _correct_user_input(string: str) -> str:
    """
    Removes everything from the string except letters, spaces and hyphens

    :param string: source string
    :return: processed string
    """
    source_string: str = string[:72]
    processed_string: str = ''
    for char in source_string:
        if char.isalpha() or char == '-':
            processed_string += char
        elif char.isspace() and (not processed_string or not processed_string[-1].isspace()):
            processed_string += char
    return processed_string


async def _format_city_data(city: dict, user_language_code: str) -> dict[str, str]:
    """
    Formats the city data

    :param city: city data
    :param user_language_code: user language code
    :return: formatted city data
    """
    city_name: str = city.get('name')
    state: str = city.get('state')
    country: str = city.get('country')
    local_names_dict: [dict | None] = city.get('local_names')
    local_name: str = city_name if local_names_dict is None else local_names_dict.get(user_language_code)
    city_local_name: str = city_name if local_name is None else local_name
    return dict(
        {
            'city_full_name': f'{city_name}, {country}' if state is None else f'{city_local_name}, {state}, {country}',
            'city_local_name': f'{city_local_name}',
            'lat': str(round(city.get('lat'), 6)),
            'lon': str(round(city.get('lon'), 6))
        }
    )


async def _get_weather_emoji(weather: int) -> str:
    """
    Returns weather code emoji from OpenWeatherMap

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


async def _format_current_weather_data(weather_data: dict,
                                       temperature_unit: str,
                                       city_local_name: str,
                                       user_language_code: str) -> str:
    """
    Returns a string with formatted weather information

    :param weather_data: dictionary with current weather data
    :param temperature_unit: temperature units
    :param city_local_name: city name in the local language
    :param user_language_code: user language code
    :return: Formatted weather data
    """
    time: str = datetime.fromtimestamp(weather_data.get('dt')).strftime('%d %b %H:%M')

    temp: int = round(weather_data.get('main').get('temp'))
    temp_units: str = '°C' if temperature_unit == 'metric' else '°F'

    temp_feels_like: int = round(weather_data.get('main').get('feels_like'))
    feels_like_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                             dialog_message_name='weather_feels_like')

    emoji: str = await _get_weather_emoji(weather=weather_data.get('weather')[0].get('id'))
    description: str = weather_data.get('weather')[0].get('description')

    humidity: int = weather_data.get('main').get('humidity')
    humidity_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                           dialog_message_name='weather_humidity')

    wind_speed: int = round(weather_data.get('wind').get('speed'))
    wind_gust: int = 0 if weather_data.get('wind').get('gust') is None else round(weather_data.get('wind').get('gust'))
    wind_units: str = 'm/s' if temperature_unit == 'metric' else 'mph'
    wind_speed_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                             dialog_message_name='weather_wind_speed')
    wind_gust_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                            dialog_message_name='weather_wind_gust')

    pressure: int = weather_data.get('main').get('pressure')
    pressure_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                           dialog_message_name='weather_pressure')

    visibility: float = round(weather_data.get('visibility') / 1000, 1)
    visibility_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                             dialog_message_name='weather_visibility')

    sunrise: str = datetime.fromtimestamp(weather_data.get('sys').get('sunrise')).strftime('%H:%M')
    sunrise_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                          dialog_message_name='weather_sunrise')
    sunset: str = datetime.fromtimestamp(weather_data.get('sys').get('sunset')).strftime('%H:%M')
    sunset_string: str = await get_dialog_message_answer(user_language_code=user_language_code,
                                                         dialog_message_name='weather_sunset')

    return f'<b>{emoji} {city_local_name}, {time}</b>\n\n' \
           f'🌡 <b>{temp} {temp_units}</b>, {feels_like_string} <b>{temp_feels_like} {temp_units}</b>, {description}\n\n' \
           f'💦 {humidity_string}: <b>{humidity} %</b>\n' \
           f'💨 {wind_speed_string}: <b>{wind_speed} {wind_units}</b>, {wind_gust_string} <b>{wind_gust} {wind_units}</b>\n' \
           f'🌡 {pressure_string}: <b>{pressure} hPa</b>\n' \
           f'🌫️ {visibility_string}: <b>{visibility} km</b>\n\n' \
           f'🌅 {sunrise_string}: <b>{sunrise}</b>, 🌇 {sunset_string} <b>{sunset}</b>'


async def get_current_weather_data(user_id: int) -> str:
    """
    Gets current weather data from the OpenWeatherMap service and outputs them in formatted form

    :param user_id: user id
    :return: formatted current weather data
    """
    settings: UserWeatherSettings = await db.get_user_settings(user_id=user_id)
    async with ClientSession() as session:
        async with session.get(url=f'{CURRENT_WEATHER_API_URL}'
                                   f'?lat={settings.latitude}'
                                   f'&lon={settings.longitude}'
                                   f'&lang={settings.lang}'
                                   f'&units={settings.units}'
                                   f'&appid={API_KEY}') as responce:
            await db.increase_api_counter()
            if responce.status == 200:
                current_weather_data: dict = await responce.json()
                return await _format_current_weather_data(
                    weather_data=current_weather_data,
                    temperature_unit=settings.units,
                    city_local_name=settings.city,
                    user_language_code=settings.lang
                )
            else:
                error: dict = await responce.json()
                logger.error('Error when requesting CurrentWeatherAPI: %s', error.get('message'))
                return await get_dialog_message_answer(user_language_code=settings.lang,
                                                       dialog_message_name='error_weather_data')


async def get_weather_forecast_data(user_id: int):
    """
    Returns the image with the weather forecast for 24 hours, in case of error - the bot logo

    :param user_id: user id
    :return:
    """
    settings: UserWeatherSettings = await db.get_user_settings(user_id=user_id)
    async with ClientSession() as session:
        async with session.get(url=f'{WEATHER_FORECAST_API_URL}'
                                   f'?lat={settings.latitude}'
                                   f'&lon={settings.longitude}'
                                   f'&lang={settings.lang}'
                                   f'&units={settings.units}'
                                   f'&cnt=8'
                                   f'&appid={API_KEY}') as responce:
            await db.increase_api_counter()
            if responce.status == 200:
                weather_forecast_data: dict = await responce.json()
                return await format_weather_forecast_image(
                    weather_data=weather_forecast_data.get('list'),
                    temperature_unit=settings.units,
                    user_id=user_id
                )
            else:
                error: dict = await responce.json()
                logger.error('Error when requesting WeatherForecastAPI: %s', error.get('message'))
                return BOT_LOGO


async def get_list_cities(city_name: str, user_language_code: str) -> list[dict[str, str]]:
    """
    Returns the list of found cities

    :param city_name: city name
    :param user_language_code: user language code
    :return: list of found cities
    """
    result: list[dict[str, str]] = []
    async with ClientSession() as session:
        async with session.get(url=f'{GEOCODING_API_URL}'
                                   f'?q={await _correct_user_input(string=city_name)}'
                                   f'&limit=5'
                                   f'&appid={API_KEY}') as responce:
            await db.increase_api_counter()
            if responce.status == 200:
                list_cities: list[dict] = await responce.json()
                if len(list_cities) != 0:
                    [result.append(await _format_city_data(city, user_language_code)) for city in list_cities]
            else:
                error: dict = await responce.json()
                logger.error('Error when requesting WeatherGeocodeAPI: %s', error.get('message'))
            return result
