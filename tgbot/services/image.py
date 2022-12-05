"""Generates an image with weather forecast information"""

from dataclasses import dataclass
from os import makedirs, path

from PIL import Image, ImageDraw, ImageFont
from PIL.PyAccess import PyAccess

from tgbot.config import BASE_DIR
from tgbot.services.classes import ForecastData


@dataclass
class Cursor:
    """Cursor to draw objects on the canvas in a loop"""

    pos_x: int = 0
    pos_y: int = 0


class DrawWeatherImage:
    """Draws an image with the weather forecast"""

    _ICONS_DIR: str = path.join(BASE_DIR, "assets/ico")
    _FONT: str = path.join(BASE_DIR, "assets/font/Rubik-Bold.ttf")
    _TEMP_DIR: str = path.join(BASE_DIR, "temp")

    def __init__(self) -> None:
        if not path.exists(self._TEMP_DIR):
            makedirs(self._TEMP_DIR)

    @staticmethod
    def _get_temp_color(temperature: str) -> str:
        """Returns the color code, depending on the temperature value"""
        if temperature[-1:] == "C":
            temp: int = int(temperature.removesuffix("°C"))
        else:
            temp = round((int(temperature.removesuffix("°F")) - 32) * (5 / 9))

        if temp >= 50:
            temp_color: str = "#2b0001"
        elif 50 > temp >= 40:
            temp_color = "#6b1527"
        elif 40 > temp >= 30:
            temp_color = "#b73466"
        elif 30 > temp >= 25:
            temp_color = "#db6c54"
        elif 25 > temp >= 20:
            temp_color = "#e09f41"
        elif 20 > temp >= 15:
            temp_color = "#e1ce39"
        elif 15 > temp >= 10:
            temp_color = "#b8db41"
        elif 10 > temp >= 5:
            temp_color = "#5ac84b"
        elif 5 > temp >= 0:
            temp_color = "#4db094"
        elif 0 > temp >= -5:
            temp_color = "#4178be"
        elif -5 > temp >= -10:
            temp_color = "#5751ac"
        elif -10 > temp >= -15:
            temp_color = "#291e6a"
        elif -15 > temp >= -20:
            temp_color = "#8e108e"
        elif -20 > temp >= -30:
            temp_color = "#f3a5f3"
        else:
            temp_color = "#e3e3e3"
        return temp_color

    @staticmethod
    def _get_wind_color(wind_speed: str) -> str:
        """Returns the color code, depending on the wind speed value"""
        if wind_speed[-1:] == "s":
            speed: int = int(wind_speed.removesuffix(" m/s"))
        else:
            speed = round(float(wind_speed.removesuffix(" mph")) / 2.237)

        if 0 <= speed < 10:
            wind_speed_color: str = "#5a5673"
        elif 10 <= speed < 20:
            wind_speed_color = "#5258ab"
        elif 20 <= speed < 30:
            wind_speed_color = "#4083b8"
        elif 30 <= speed < 40:
            wind_speed_color = "#4ea98f"
        elif 40 <= speed < 50:
            wind_speed_color = "#4abe47"
        elif 50 <= speed < 60:
            wind_speed_color = "#8ec94b"
        elif 60 <= speed < 70:
            wind_speed_color = "#cad63e"
        elif 70 <= speed < 80:
            wind_speed_color = "#d8bf3d"
        elif 80 <= speed < 90:
            wind_speed_color = "#d69b44"
        elif 90 <= speed < 100:
            wind_speed_color = "#d5784c"
        elif 100 <= speed < 110:
            wind_speed_color = "#c7466f"
        elif 110 <= speed < 120:
            wind_speed_color = "#a3355b"
        elif 120 <= speed < 130:
            wind_speed_color = "#901c4f"
        elif 130 <= speed < 140:
            wind_speed_color = "#631a1b"
        else:
            wind_speed_color = "#2b0001"
        return wind_speed_color

    @staticmethod
    def _get_color_of_text_temperature(temperature: str) -> str:
        """Returns the temperature text color code, depending on the temperature value"""
        if temperature[-1:] == "C":
            temp: int = int(temperature.removesuffix("°C"))
        else:
            temp = round((int(temperature.removesuffix("°F")) - 32) * (5 / 9))

        if 20 >= temp >= 0 or temp <= -30:
            return "#000000"
        return "#FFFFFF"

    @staticmethod
    def _get_color_of_text_wind(wind_speed: str) -> str:
        """Returns the wind speed text color code, depending on the wind speed value"""
        if wind_speed[-1:] == "s":
            speed: int = int(wind_speed.removesuffix(" m/s"))
        else:
            speed = round(float(wind_speed.removesuffix(" mph")) / 2.237)

        if 90 >= speed >= 40:
            return "#000000"
        return "#FFFFFF"

    @staticmethod
    def _invert_image_color(image: Image) -> Image:
        """Inverts the black color in the image"""
        pixel_data: PyAccess | None = image.load()
        size_x, size_y = image.size
        for pos_y in range(size_y):
            for pos_x in range(size_x):
                if pixel_data:
                    alpha = pixel_data[pos_x, pos_y][3]
                    if alpha:
                        pixel_data[pos_x, pos_y] = (255, 255, 255, alpha)
        return image

    def draw_image(self, data: ForecastData, user_id: int) -> str:
        """Draws an image with weather forecast information"""
        cursor: Cursor = Cursor()
        canvas: Image = Image.new(mode="RGBA", size=(799, 199), color="#262626")
        draw: ImageDraw = ImageDraw.Draw(im=canvas)

        temp: list[str] = data.temp
        time: list[str] = data.time
        ico_code: list[str] = data.ico_code
        wind_speed: list[str] = data.wind_speed

        def draw_text_align_center(pos_x: int, pos_y: int, font_size: int, text: str, color: str) -> None:
            """Draws specified text with center alignment"""
            font: ImageFont = ImageFont.truetype(font=self._FONT, size=font_size)
            offset: int = round((99 - draw.textlength(text=text, font=font)) / 2)
            draw.text(xy=(pos_x + offset, pos_y), text=text, font=font, fill=color)

        for idx in range(8):
            # fill temperature columns
            cursor.pos_y = 0
            draw.rectangle(
                xy=(cursor.pos_x, cursor.pos_y, cursor.pos_x + 98, cursor.pos_y + 163),
                fill=self._get_temp_color(temperature=temp[idx]),
            )
            # draw time
            color_of_text: str = self._get_color_of_text_temperature(temperature=temp[idx])
            cursor.pos_y = 15
            draw_text_align_center(
                pos_x=cursor.pos_x, pos_y=cursor.pos_y, font_size=24, text=time[idx], color=color_of_text
            )
            # draw weather icons
            cursor.pos_y = 50
            file_path: str = path.join(self._ICONS_DIR, f"{ico_code[idx]}.png")
            weather_icon: Image = Image.open(fp=file_path, mode="r", formats=("PNG",))
            if color_of_text == "#FFFFFF":
                weather_icon = self._invert_image_color(image=weather_icon)
            canvas.alpha_composite(im=weather_icon, dest=(cursor.pos_x + 17, cursor.pos_y))
            weather_icon.close()
            # draw temperature
            cursor.pos_y = 126
            draw_text_align_center(
                pos_x=cursor.pos_x, pos_y=cursor.pos_y, font_size=24, text=temp[idx], color=color_of_text
            )
            # fill wind speed columns
            cursor.pos_y = 165
            draw.rectangle(
                xy=(cursor.pos_x, cursor.pos_y, cursor.pos_x + 98, cursor.pos_y + 34),
                fill=self._get_wind_color(wind_speed=wind_speed[idx]),
            )
            # draw wind speed
            color_of_text = self._get_color_of_text_wind(wind_speed=wind_speed[idx])
            cursor.pos_y = 173
            draw_text_align_center(
                pos_x=cursor.pos_x, pos_y=cursor.pos_y, font_size=18, text=wind_speed[idx], color=color_of_text
            )
            # shift to the next column
            cursor.pos_x += 100

        path_to_image: str = path.join(self._TEMP_DIR, f"{user_id}.png")
        canvas.save(fp=path_to_image, format="PNG")
        canvas.close()

        return path_to_image
