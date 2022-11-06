""" Creates inline keyboards for dialogs with the bot """

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.misc.locale import get_dialog_message_answer


async def generate_cities_keyboard(cities: list[dict], user_language_code: str) -> InlineKeyboardMarkup:
    """
    Generates a keyboard containing buttons with cities and their coordinates

    :param cities: list of cities
    :param user_language_code: user language code
    :return: Generated keyboard (object of InlineKeyboardMarkup class)
    """
    keyboard_cities: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    for city in cities:
        keyboard_cities.insert(InlineKeyboardButton(
            text=city.get('city_full_name'),
            callback_data=f'city_coords_and_name={city.get("lat")}&{city.get("lon")}&{city.get("city_local_name")}')
        )
    keyboard_cities.insert(InlineKeyboardButton(
        text=await get_dialog_message_answer(user_language_code=user_language_code,
                                             dialog_message_name='dialog_input_another_city'),
        callback_data=f'input_another_city')
    )
    return keyboard_cities


async def generate_temperature_units_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard with temperature unit selection buttons

    :return: Generated keyboard (object of InlineKeyboardMarkup class)
    """
    keyboard_temperature_units: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)
    keyboard_temperature_units.insert(InlineKeyboardButton(text='°C', callback_data='temperature_units=c'))
    keyboard_temperature_units.insert(InlineKeyboardButton(text='°F', callback_data='temperature_units=f'))
    return keyboard_temperature_units
