""" Creates inline keyboards for dialogs with the bot """

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.models.localization import locale
from tgbot.services.weather_formatter import CityData


async def gen_cities_kb(cities: list[CityData], lang: str) -> InlineKeyboardMarkup:
    """
    Creates a keyboard containing buttons with cities and their coordinates

    :param cities: list of cities
    :param lang: user language code
    :return: Generated keyboard (object of InlineKeyboardMarkup class)
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    for city in cities:
        keyboard.insert(InlineKeyboardButton(
            text=city.full_name,
            callback_data=f'city_data={city.latitude}&{city.longitude}&{city.name}')
        )
    keyboard.insert(InlineKeyboardButton(
        text=await locale.get_translate(lang=lang, translate='another_city'),
        callback_data=f'another_city')
    )
    return keyboard


async def gen_units_kb() -> InlineKeyboardMarkup:
    """
    Creates a keyboard with measurement unit selection buttons

    :return: Generated keyboard (object of InlineKeyboardMarkup class)
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(InlineKeyboardButton(text='°C', callback_data='units=c'))
    keyboard.insert(InlineKeyboardButton(text='°F', callback_data='units=f'))
    return keyboard


async def gen_admin_kb(lang: str) -> InlineKeyboardMarkup:
    """
    Creates a keyboard for administrators

    :return: Generated keyboard (object of InlineKeyboardMarkup class)
    """
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    keyboard.insert(InlineKeyboardButton(
        text=await locale.get_translate(lang=lang, translate='admin_keyboard'),
        callback_data='admin')
    )
    return keyboard
