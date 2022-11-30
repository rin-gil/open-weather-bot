"""Creates reply keyboards for dialogs with the bot"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.middlewares.localization import i18n


_ = i18n.gettext  # Alias for gettext method


async def create_geolocation_kb(lang_code: str) -> ReplyKeyboardMarkup:
    """Creates a keyboard for sending geolocation"""
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.insert(KeyboardButton(text="📍 " + _("Send geolocation", locale=lang_code), request_location=True))
    return keyboard
