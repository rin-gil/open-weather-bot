"""Other message handlers"""

from asyncio import sleep

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, Message

from tgbot.config import BOT_LOGO
from tgbot.handlers.dialog import delete_previous_dialog_message
from tgbot.middlewares.localization import i18n
from tgbot.services.database import database

_ = i18n.gettext  # Alias for gettext method


async def if_user_sent_command_about(message: Message) -> None:
    """Handles command /about from the user"""
    await message.delete()
    user_lang_code: str = message.from_user.language_code
    bot_answer_text: str = (
        "🤖 <b>OpenWeatherBot</b> "
        + _("is written in", locale=user_lang_code)
        + " <b>Python</b> "
        + _("using the", locale=user_lang_code)
        + " <b>AIOgram</b> "
        + _("library", locale=user_lang_code)
        + "\n\n"
        + _("Weather data provided by", locale=user_lang_code)
        + ' <a href="https://openweathermap.org/">OpenWeather</a>\n'
        + _("Icon by", locale=user_lang_code)
        + ' <a href="https://freeicons.io/profile/2257">www.wishforge.games</a> '
        + _("on", locale=user_lang_code)
        + ' <a href="https://freeicons.io">freeicons.io</a>\n'
        + _("The source code is available on", locale=user_lang_code)
        + ' <a href="https://github.com/rin-gil/OpenWeatherBot">GitHub</a>'
    )
    bot_answer: Message = await message.answer_photo(
        photo=InputFile(BOT_LOGO), caption=bot_answer_text, reply_markup=None
    )
    await sleep(15)
    await message.bot.delete_message(chat_id=bot_answer.chat.id, message_id=bot_answer.message_id)


async def if_user_sent_command_stop(message: Message, state: FSMContext) -> None:
    """Handles command /stop from the user"""
    user_lang_code: str = message.from_user.language_code
    await delete_previous_dialog_message(obj=message)
    await state.reset_state()
    await database.delete_user(user_id=message.from_user.id)
    bot_answer_text: str = "❌ " + _("All of your data has been deleted", locale=user_lang_code)
    bot_answer: Message = await message.answer_photo(
        photo=InputFile(BOT_LOGO), caption=bot_answer_text, reply_markup=None
    )
    await sleep(5)
    await message.bot.delete_message(chat_id=bot_answer.chat.id, message_id=bot_answer.message_id)


def register_other_handlers(dp: Dispatcher) -> None:
    """Registers other handlers"""
    dp.register_message_handler(if_user_sent_command_about, commands="about", state="*")
    dp.register_message_handler(if_user_sent_command_stop, commands="stop", state="*")
