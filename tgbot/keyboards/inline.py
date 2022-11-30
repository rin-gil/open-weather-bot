""" Creates inline keyboards for dialogs with the bot """

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.middlewares.localization import i18n
from tgbot.services.classes import CityData


_ = i18n.gettext  # Alias for gettext method


async def create_city_selection_kb(list_cities: list[CityData], lang_code: str) -> InlineKeyboardMarkup:
    """Creates a keyboard containing buttons with cities and their coordinates"""
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    for city in list_cities:
        keyboard.insert(
            InlineKeyboardButton(
                text=city.full_name,
                # cut city.name to 35, because the max length of callback_data is 64
                callback_data=f"data={city.latitude}&{city.longitude}&{city.name[:35]}",
            )
        )
    keyboard.insert(
        InlineKeyboardButton(text="◀️ " + _("Select another city", locale=lang_code), callback_data="another_city")
    )
    return keyboard


async def create_units_selection_kb() -> InlineKeyboardMarkup:
    """Creates a keyboard with measurement unit selection buttons"""
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(InlineKeyboardButton(text="°C", callback_data="units=c"))
    keyboard.insert(InlineKeyboardButton(text="°F", callback_data="units=f"))
    return keyboard
