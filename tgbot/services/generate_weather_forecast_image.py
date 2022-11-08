""" Generates an image with weather forecast information """

from dataclasses import dataclass
from datetime import datetime
from os import path

from PIL import Image, ImageDraw, ImageFont

from tgbot.config import BASE_DIR

WEATHER_ICON_DIR: str = path.join(BASE_DIR, 'assets/ico')
FONT: str = path.join(BASE_DIR, 'assets/font/Rubik-Bold.ttf')
FORECAST_IMAGE_DIR: str = path.join(BASE_DIR, 'temp')


@dataclass
class Cursor:
    """ Cursor to draw objects on the canvas in a loop """
    x: int = 0
    y: int = 0


def _get_temperature_color(temperature: str) -> str:
    """
    Returns the color code, depending on the temperature value

    :param temperature: temperature
    :return: hex color code
    """
    if temperature[-1:] == 'C':
        temp: int = int(temperature.removesuffix('°C'))
    else:
        temp: int = round((int(temperature.removesuffix('°F')) - 32) * (5 / 9))

    if temp >= 50:
        return '#2b0001'
    if 50 > temp >= 40:
        return '#6b1527'
    if 40 > temp >= 30:
        return '#b73466'
    if 30 > temp >= 25:
        return '#db6c54'
    if 25 > temp >= 20:
        return '#e09f41'
    if 20 > temp >= 15:
        return '#e1ce39'
    if 15 > temp >= 10:
        return '#b8db41'
    if 10 > temp >= 5:
        return '#5ac84b'
    if 5 > temp >= 0:
        return '#4db094'
    if 0 > temp >= -5:
        return '#4178be'
    if -5 > temp >= -10:
        return '#5751ac'
    if -10 > temp >= -15:
        return '#291e6a'
    if -15 > temp >= -20:
        return '#8e108e'
    if -20 > temp >= -30:
        return '#f3a5f3'
    if -30 > temp:
        return '#e3e3e3'


def _get_wind_speed_color(wind_speed: str) -> str:
    """
    Returns the color code, depending on the wind speed value

    :param wind_speed: wind speed
    :return: hex color code
    """
    if wind_speed[-1:] == 's':
        speed: int = int(wind_speed.removesuffix(' m/s'))
    else:
        speed: int = round(float(wind_speed.removesuffix(' mph')) / 2.237)

    if 0 <= speed < 10:
        return '#5a5673'
    if 10 <= speed < 20:
        return '#5258ab'
    if 20 <= speed < 30:
        return '#4083b8'
    if 30 <= speed < 40:
        return '#4ea98f'
    if 40 <= speed < 50:
        return '#4abe47'
    if 50 <= speed < 60:
        return '#8ec94b'
    if 60 <= speed < 70:
        return '#cad63e'
    if 70 <= speed < 80:
        return '#d8bf3d'
    if 80 <= speed < 90:
        return '#d69b44'
    if 90 <= speed < 100:
        return '#d5784c'
    if 100 <= speed < 110:
        return '#c7466f'
    if 110 <= speed < 120:
        return '#a3355b'
    if 120 <= speed < 130:
        return '#901c4f'
    if 130 <= speed < 140:
        return '#631a1b'
    if 140 <= speed:
        return '#2b0001'


async def _generate_weather_forecast_image(forecast_data: dict[str, list[str]], user_id: int) -> str:
    width: int = 807 - 1
    height: int = 200 - 1
    cursor: Cursor = Cursor()
    canvas: Image = Image.new(mode='RGBA', size=(width, height), color='#262626')
    draw: ImageDraw = ImageDraw.Draw(im=canvas)

    forecast_temp: list = forecast_data.get('forecast_temp')
    forecast_time: list = forecast_data.get('forecast_time')
    forecast_ico_code: list = forecast_data.get('forecast_ico_code')
    forecast_wind_speed: list = forecast_data.get('forecast_wind_speed')

    for index in range(8):
        # fill temperature columns
        cursor.y = 0
        draw.rectangle(xy=(cursor.x, cursor.y, cursor.x + 99, cursor.y + 163),
                       fill=_get_temperature_color(temperature=forecast_temp[index]))
        # draw time
        cursor.y = 15
        font: ImageFont = ImageFont.truetype(font=FONT, size=24)
        text = forecast_time[index]
        offset: int = round((100 - draw.textlength(text=text, font=font)) / 2)
        draw.text(xy=(cursor.x + offset, cursor.y), text=text, font=font, fill='#000000')
        # draw weather icons
        cursor.y = 50
        file_path: str = path.join(WEATHER_ICON_DIR, f'{forecast_ico_code[index]}.png')
        img: Image = Image.open(fp=file_path, mode='r', formats=('PNG',))
        canvas.alpha_composite(im=img, dest=(cursor.x + 18, cursor.y))
        img.close()
        # draw temperature
        cursor.y = 126
        text = forecast_temp[index]
        offset: int = round((100 - draw.textlength(text=text, font=font)) / 2)
        draw.text(xy=(cursor.x + offset, cursor.y), text=text, font=font, fill='#000000')
        # fill wind speed columns
        cursor.y = 165
        draw.rectangle(xy=(cursor.x, cursor.y, cursor.x + 99, cursor.y + 34),
                       fill=_get_wind_speed_color(wind_speed=forecast_wind_speed[index]))
        # draw wind speed
        cursor.y = 173
        font: ImageFont = ImageFont.truetype(font=FONT, size=18)
        text = forecast_wind_speed[index]
        offset: int = round((100 - draw.textlength(text=text, font=font)) / 2)
        draw.text(xy=(cursor.x + offset, cursor.y), text=text, font=font, fill='#000000')

        cursor.x += 101

    forecast_image_path: str = path.join(FORECAST_IMAGE_DIR, f'{user_id}.png')
    canvas.save(fp=forecast_image_path, format='PNG')
    canvas.close()

    return forecast_image_path


async def format_weather_forecast_image(weather_data: list[dict], temperature_unit: str, user_id: int):
    """
    Formats the data for generating the weather forecast image

    :param user_id: user id
    :param weather_data: weather data from the weather api request
    :param temperature_unit: temperature units
    :return: the path to the file with the weather forecast image
    """
    forecast_time: list = []
    forecast_ico_code: list = []
    forecast_temp: list = []
    forecast_wind_speed: list = []
    temp_units: str = '°C' if temperature_unit == 'metric' else '°F'
    wind_units: str = 'm/s' if temperature_unit == 'metric' else 'mph'
    for data in weather_data:
        forecast_time.append(datetime.fromtimestamp(data.get('dt')).strftime('%H:%M'))
        forecast_ico_code.append(data.get('weather')[0].get('icon'))
        forecast_temp.append(f'{round(data.get("main").get("temp"))}{temp_units}')
        forecast_wind_speed.append(f'{round(data.get("wind").get("speed"))} {wind_units}')
    forecast_data: dict[str, list[str]] = {
        "forecast_time": forecast_time,
        "forecast_ico_code": forecast_ico_code,
        "forecast_temp": forecast_temp,
        "forecast_wind_speed": forecast_wind_speed
    }

    return await _generate_weather_forecast_image(forecast_data=forecast_data, user_id=user_id)
