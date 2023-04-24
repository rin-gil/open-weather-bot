""" Handling messages from bot users """

from asyncio import sleep
from os import remove as os_remove

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, InlineKeyboardMarkup, InputFile, Message, ReplyKeyboardMarkup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from tgbot.config import BOT_LOGO
from tgbot.keyboards.inline import create_city_selection_kb, create_units_selection_kb
from tgbot.keyboards.reply import create_geolocation_kb
from tgbot.middlewares.localization import i18n
from tgbot.misc.states import WeatherSetupDialog
from tgbot.services.database import database
from tgbot.services.classes import CityData
from tgbot.services.weather import weather


_ = i18n.gettext  # Alias for gettext method


async def delete_previous_dialog_message(obj: Message | CallbackQuery) -> None:
    """Deletes the previous dialog message, if it exists"""
    if isinstance(obj, Message):
        await obj.delete()
    else:
        await obj.answer(cache_time=1)
    user_id: int = obj.from_user.id
    dialog_id: int | None = await database.get_dialog_id_if_exists(user_id=user_id)
    if dialog_id:
        try:
            await obj.bot.delete_message(chat_id=user_id, message_id=dialog_id)
        except MessageToDeleteNotFound:
            pass


async def dialog_start(message: Message, state: FSMContext) -> None:
    """Handles command /start from the user"""
    user_lang_code: str = message.from_user.language_code
    user_id: int = message.from_user.id
    await delete_previous_dialog_message(obj=message)
    await state.reset_state()
    await database.delete_user(user_id=message.from_user.id)
    dialog_text: str = (
        _("Let's set the weather!", locale=user_lang_code)
        + " 🌦\n\n"
        + _("Write the name of the city or send your coordinates", locale=user_lang_code)
        + ":"
    )
    dialog: Message = await message.answer_photo(
        photo=InputFile(BOT_LOGO),
        caption=dialog_text,
        disable_notification=True,
        reply_markup=await create_geolocation_kb(lang_code=user_lang_code),
    )
    await database.save_dialog_id(user_id=user_id, dialog_id=dialog.message_id)
    await WeatherSetupDialog.EnterCityName.set()


async def dialog_select_city(message: Message) -> None:
    """Handling of city search results by geolocation or address"""
    user_lang_code: str = message.from_user.language_code
    user_id: int = message.from_user.id
    await delete_previous_dialog_message(obj=message)
    await WeatherSetupDialog.previous()  # Block user input while city search is being processed
    if message.content_type in ("location", "venue"):  # If the user sent geolocation
        list_found_cities: list[CityData] | None = await weather.get_list_cities(
            city_name_or_location=message.location, lang_code=user_lang_code
        )
    else:  # If the user sent the city name
        list_found_cities = await weather.get_list_cities(city_name_or_location=message.text, lang_code=user_lang_code)
    if list_found_cities:  # If cities are found
        dialog_text: str = "🏙 " + _("Select the desired city", locale=user_lang_code) + ":"
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup = await create_city_selection_kb(
            list_cities=list_found_cities, lang_code=user_lang_code
        )
    else:  # If no cities are found
        dialog_text = (
            "❌ "
            + _("I couldn't find a single city!", locale=user_lang_code)
            + "\n\n"
            + _("Try changing the name of the city", locale=user_lang_code)
            + ":"
        )
        reply_markup = await create_geolocation_kb(lang_code=user_lang_code)
        await WeatherSetupDialog.EnterCityName.set()  # Unblock user input for another city name
    dialog: Message = await message.answer_photo(
        photo=InputFile(BOT_LOGO), caption=dialog_text, disable_notification=True, reply_markup=reply_markup
    )
    await database.save_dialog_id(user_id=user_id, dialog_id=dialog.message_id)


async def dialog_select_another_city(call: CallbackQuery) -> None:
    """Returns to the input of the city name"""
    user_lang_code: str = call.from_user.language_code
    user_id: int = call.from_user.id
    await delete_previous_dialog_message(obj=call)
    dialog: Message = await call.message.answer_photo(
        photo=InputFile(BOT_LOGO),
        caption=_("Write the name of the city or send your coordinates", locale=user_lang_code) + ":",
        disable_notification=True,
        reply_markup=await create_geolocation_kb(lang_code=user_lang_code),
    )
    await database.save_dialog_id(user_id=user_id, dialog_id=dialog.message_id)
    await WeatherSetupDialog.EnterCityName.set()


async def dialog_select_measure_units(call: CallbackQuery) -> None:
    """Processes the coordinates of the selected user city and displays a dialog to select the temperature units"""
    user_lang_code: str = call.from_user.language_code
    user_id: int = call.from_user.id
    await delete_previous_dialog_message(obj=call)
    dialog: Message = await call.message.answer_photo(
        photo=InputFile(BOT_LOGO),
        caption="🌡 " + _("Choose units of temperature measurement", locale=user_lang_code) + ":",
        disable_notification=True,
        reply_markup=await create_units_selection_kb(),
    )
    await database.save_dialog_id(user_id=user_id, dialog_id=dialog.message_id)
    latitude, longitude, city = call.data.removeprefix("data=").split("&")
    await database.save_city_coords(user_id=user_id, city=city, latitude=float(latitude), longitude=float(longitude))


async def dialog_finish(call: CallbackQuery, state: FSMContext) -> None:
    """Saves the language and units in the database, completes the weather setup dialog"""
    user_lang_code: str = call.from_user.language_code
    user_id: int = call.from_user.id
    await delete_previous_dialog_message(obj=call)
    measure_units: str = "metric" if call.data.removeprefix("units=") == "c" else "imperial"
    await database.save_user_settings(user_id=user_id, lang_code=user_lang_code, measure_units=measure_units)
    weather_forecast: str = await weather.get_weather_forecast(user_id=user_id)
    dialog: Message = await call.message.answer_photo(
        photo=InputFile(weather_forecast),
        caption=await weather.get_current_weather(user_id=user_id),
        disable_notification=True,
    )
    if weather_forecast[-12:-4] != "bot_logo":
        os_remove(weather_forecast)
    await database.save_dialog_id(user_id=user_id, dialog_id=dialog.message_id)
    final_message_text: str = (
        "🌥 "
        + _("The weather setup is complete", locale=user_lang_code)
        + "\n\n"
        + _("The data will be updated automatically every 3 hours", locale=user_lang_code)
    )
    final_message: Message = await call.message.answer(
        text=f"<code>{final_message_text}</code>", disable_notification=True
    )
    await sleep(15)
    await call.bot.delete_message(chat_id=call.message.chat.id, message_id=final_message.message_id)
    await state.reset_state()


async def any_other_messages(message: Message) -> None:
    """Deletes unprocessed messages or commands from the user"""
    await message.delete()


def register_dialog_handlers(dp: Dispatcher) -> None:
    """Registers dialog handlers"""
    dp.register_message_handler(dialog_start, commands="start", state="*")
    dp.register_message_handler(
        dialog_select_city, content_types=["text", "location", "venue"], state=WeatherSetupDialog.EnterCityName
    )
    dp.register_callback_query_handler(dialog_select_another_city, text="another_city", state="*")
    dp.register_callback_query_handler(dialog_select_measure_units, text_contains="data=", state="*")
    dp.register_callback_query_handler(dialog_finish, text_contains="units=", state="*")
    dp.register_message_handler(any_other_messages, state="*", content_types=ContentTypes.ANY)
