""" Handling messages from bot users """

from os import remove

from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile, Message
from aiogram.utils.exceptions import MessageIdentifierNotSpecified, MessageToDeleteNotFound

from tgbot.config import BOT_LOGO
from tgbot.keyboards.inline import gen_cities_kb, gen_units_kb
from tgbot.misc.states import UserInput
from tgbot.models.database import database
from tgbot.models.localization import locale
from tgbot.services.weather_api import weather
from tgbot.services.weather_formatter import CityData


async def _del_old_dialog_message_and_send_new(message: Message, old_dialog_message_id: int, message_text: str) -> int:
    """
    Implement the dialog logic in a single message:
        Deletes the old dialog message and sends a new one. Returns the id of the new message.

    :param message: message from the user
    :param old_dialog_message_id: old message id
    :param message_text: the text to be sent to the user
    :return: old message id or new message id
    """
    try:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=old_dialog_message_id)
    except MessageToDeleteNotFound:
        pass
    except MessageIdentifierNotSpecified:
        pass
    new_dialog_message: Message = await message.answer(text=message_text)
    return new_dialog_message.message_id


async def start(message: Message, state: FSMContext) -> None:
    """
    Handles command /start from the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await message.delete()
    await state.reset_state()
    async with state.proxy() as data:
        data['id']: int = message.from_user.id
        data['lang']: str = message.from_user.language_code
        data['dialog_message_id']: int = await _del_old_dialog_message_and_send_new(
            message=message,
            old_dialog_message_id=await database.get_dialog_message_id(user_id=data['id']),
            message_text=await locale.get_translate(lang=data['lang'], translate='start')
        )
    await UserInput.Allow.set()  # Allow user input
    await database.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])


async def about(message: Message) -> None:
    """
    Handles command /about from the user

    :param message: message from the user
    :return: None
    """
    await message.delete()
    text: str = '🤖 <b>OpenWeatherBot</b> is written in <b>Python</b> using the <b>AIOgram</b> library.\n\n' \
                'Weather data provided by <a href="https://openweathermap.org/">OpenWeather</a>\n' \
                'Icon by <a href="https://freeicons.io/profile/2257">www.wishforge.games</a> on ' \
                '<a href="https://freeicons.io">freeicons.io</a>\n' \
                'The source code is available on <a href="https://github.com/rin-gil/OpenWeatherBot">GitHub</a>'
    about_message = await message.bot.send_photo(chat_id=message.from_user.id, photo=InputFile(BOT_LOGO), caption=text)
    await sleep(15)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=about_message.message_id)


async def stop(message: Message, state: FSMContext) -> None:
    """
    Handles command /stop from the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await message.delete()
    await state.reset_state()
    async with state.proxy() as data:
        data.clear()
    dialog_message_id: int = await _del_old_dialog_message_and_send_new(
        message=message,
        old_dialog_message_id=await database.get_dialog_message_id(user_id=message.from_user.id),
        message_text=await locale.get_translate(lang=message.from_user.language_code, translate='stop'))
    await database.delete_user(user_id=message.from_user.id)
    await sleep(5)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=dialog_message_id)


async def select_city(message: types.Message, state: FSMContext) -> None:
    """
    Processing the result of the search of the city entered by the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await message.delete()
    await UserInput.previous()  # Deny user input (prevents repeated city search if OpenWeatherMap API service
    #                             takes a long time to process the request)
    async with state.proxy() as data:
        await message.bot.edit_message_text(
            text=await locale.get_translate(lang=data['lang'], translate='select_city'),
            chat_id=data['id'],
            message_id=data['dialog_message_id']
        )
        cities_found: list[CityData] = await weather.get_cities(city_name=message.text, lang=data['lang'])
        if len(cities_found) == 0:
            await message.bot.edit_message_text(
                text=await locale.get_translate(lang=data['lang'], translate='select_city_error'),
                chat_id=data['id'],
                message_id=data['dialog_message_id']
            )
            await UserInput.Allow.set()  # Allow user input
        else:
            await message.bot.edit_message_text(
                text=await locale.get_translate(lang=data['lang'], translate='select_city_success'),
                chat_id=data['id'],
                message_id=data['dialog_message_id'],
                reply_markup=await gen_cities_kb(cities=cities_found, lang=data['lang'])
            )


async def another_city(call: CallbackQuery) -> None:
    """
    Returns to the input of the city name

    :param call: CallbackQuery
    :return: None
    """
    await call.answer(cache_time=1)
    await call.bot.edit_message_text(
        text=await locale.get_translate(lang=call.from_user.language_code, translate='start'),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    await UserInput.Allow.set()  # Allow user input


async def choice_units(call: CallbackQuery, state: FSMContext) -> None:
    """
    Processes the coordinates of the selected user city and displays a dialog to select the temperature units

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    await call.answer(cache_time=1)
    async with state.proxy() as data:
        city_data: str = call.data.removeprefix('city_data=')
        latitude, longitude, city = city_data.split('&')
        data['latitude'], data['longitude'], data['city'] = float(latitude), float(longitude), city
        await call.bot.edit_message_text(
            text=await locale.get_translate(lang=call.from_user.language_code, translate='choice_units'),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=await gen_units_kb()
        )


async def save_settings(call: CallbackQuery, state: FSMContext) -> None:
    """
    Saves the user's weather settings in the database

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    await call.answer(text=await locale.get_translate(lang=call.from_user.language_code, translate='save_settings'),
                      show_alert=True,
                      cache_time=1)

    async with state.proxy() as data:
        data['units']: str = 'metric' if call.data.removeprefix('units=') == 'c' else 'imperial'
        await database.save_user_settings(settings=data.as_dict())
        await call.bot.edit_message_text(
            text=await locale.get_translate(lang=call.from_user.language_code, translate='loading_data'),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        path_to_forecast_image: str = await weather.get_weather_forecast(user_id=call.message.chat.id)
        new_dialog_message: Message = await call.bot.send_photo(
            chat_id=call.message.chat.id,
            photo=InputFile(path_to_forecast_image),
            caption=await weather.get_current_weather(user_id=call.message.chat.id)
        )
        remove(path_to_forecast_image)
        await call.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await database.save_dialog_message_id(user_id=call.message.chat.id,
                                              dialog_message_id=new_dialog_message.message_id)
        data.clear()


async def unprocessed(message: Message) -> None:
    """
    Deletes unprocessed messages or commands from the user

    :param message: message from the user
    :return: None
    """
    await message.delete()


def register_user(dp: Dispatcher) -> None:
    """
    Registers the handling of commands from the user in the Dispatcher.

    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(start, commands='start', state='*')
    dp.register_message_handler(about, commands='about', state='*')
    dp.register_message_handler(stop, commands='stop', state='*')
    dp.register_message_handler(select_city, state=UserInput.Allow)
    dp.register_callback_query_handler(another_city, text='another_city')
    dp.register_callback_query_handler(choice_units, text_contains='city_data=')
    dp.register_callback_query_handler(save_settings, text_contains='units=')
    dp.register_message_handler(unprocessed, state='*', content_types=types.ContentTypes.ANY)
