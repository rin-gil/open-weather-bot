""" Generates an image with weather forecast information """

from datetime import datetime


async def format_weather_forecast_image(weather_data: list[dict],
                                        temperature_unit: str,
                                        city_local_name: str,
                                        user_language_code: str):
    temp_units: str = '°C' if temperature_unit == 'metric' else '°F'
    wind_units: str = 'm/s' if temperature_unit == 'metric' else 'mph'
    for data in weather_data:
        time: str = datetime.fromtimestamp(data.get('dt')).strftime('%H:%M')
        temp: int = round(data.get('main').get('temp'))
        weather_ico_code: str = data.get('weather')[0].get('icon')
        wind_speed: int = round(data.get('wind').get('speed'))
    return 'https://i.ibb.co/2tP1VVh/stub-image.png'
