""" Handling messages from bot users """

from os import remove

from asyncio import sleep

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentTypes, InputFile, Message
from aiogram.utils.exceptions import MessageIdentifierNotSpecified, MessageToDeleteNotFound

from tgbot.config import BOT_LOGO
from tgbot.keyboards.inline import gen_cities_kb, gen_units_kb
from tgbot.misc.logging import logger
from tgbot.misc.states import UserInput
from tgbot.models.database import database
from tgbot.models.localization import locale
from tgbot.services.weather_api import weather
from tgbot.services.weather_formatter import CityData


async def delete_reply_message(message: Message, reply_id: int) -> None:
    """
    Deletes the message that came from the user and the bots previous reply

    :param message: message from the user
    :param reply_id: the id of bot reply to be deleted
    :return: None
    """
    try:
        await message.delete()
    except MessageToDeleteNotFound as ex:
        logger.debug(ex)
    try:
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=reply_id)
    except MessageToDeleteNotFound as ex:
        logger.debug(ex)
    except MessageIdentifierNotSpecified as ex:
        logger.debug(ex)


async def delete_reply_call(call: CallbackQuery, reply_id: int) -> None:
    """
    Deletes the bots previous reply

    :param call: CallbackQuery
    :param reply_id: the id of bot reply to be deleted
    :return: None
    """
    try:
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=reply_id)
    except MessageToDeleteNotFound as ex:
        logger.debug(ex)
    except MessageIdentifierNotSpecified as ex:
        logger.debug(ex)


async def start(message: Message, state: FSMContext) -> None:
    """
    Handles command /start from the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await state.reset_state(with_data=True)
    async with state.proxy() as data:
        data['id']: int = message.from_user.id
        data['lang']: str = message.from_user.language_code
        await delete_reply_message(message=message, reply_id=await database.get_dialog_message_id(user_id=data['id']))
        reply = await message.answer_photo(photo=InputFile(BOT_LOGO),
                                           caption=await locale.get_translate(lang=data['lang'], translate='start'),
                                           disable_notification=True)
        data['dialog_message_id']: int = reply.message_id
    await UserInput.Allow.set()  # Allow user input
    await database.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])


async def about(message: Message) -> None:
    """
    Handles command /about from the user

    :param message: message from the user
    :return: None
    """
    await message.delete()
    text: str = '🤖 <b>OpenWeatherBot</b> is written in <b>Python</b> using the <b>AIOgram</b> library\n\n' \
                'Weather data provided by <a href="https://openweathermap.org/">OpenWeather</a>\n' \
                'Icon by <a href="https://freeicons.io/profile/2257">www.wishforge.games</a> on ' \
                '<a href="https://freeicons.io">freeicons.io</a>\n' \
                'The source code is available on <a href="https://github.com/rin-gil/OpenWeatherBot">GitHub</a>'
    reply = await message.answer_photo(photo=InputFile(BOT_LOGO), caption=text, disable_notification=True)
    await sleep(15)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=reply.message_id)


async def stop(message: Message, state: FSMContext) -> None:
    """
    Handles command /stop from the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await delete_reply_message(message=message,
                               reply_id=await database.get_dialog_message_id(user_id=message.from_user.id))
    await state.reset_state(with_data=True)
    reply = await message.answer_photo(
        photo=InputFile(BOT_LOGO),
        caption=await locale.get_translate(lang=message.from_user.language_code, translate='stop'),
        disable_notification=True
    )
    await database.delete_user(user_id=message.from_user.id)
    await sleep(5)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=reply.message_id)


async def select_city(message: Message, state: FSMContext) -> None:
    """
    Processing the result of the search of the city entered by the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await UserInput.previous()  # Prevent user input
    async with state.proxy() as data:
        await delete_reply_message(message=message, reply_id=data['dialog_message_id'])
        reply = await message.answer_photo(
            photo=InputFile(BOT_LOGO),
            caption=await locale.get_translate(lang=data['lang'], translate='select_city'),
            disable_notification=True
        )
        data['dialog_message_id'] = reply.message_id
        if message.content_type == 'location' or message.content_type == 'venue':
            cities_found: list[CityData] = await weather.get_cities(lang=data['lang'],
                                                                    latitude=message.location.latitude,
                                                                    longitude=message.location.longitude)
        else:
            cities_found: list[CityData] = await weather.get_cities(lang=data['lang'], city_name=message.text)
        if len(cities_found) == 0:
            await delete_reply_message(message=message, reply_id=data['dialog_message_id'])
            reply = await message.answer_photo(
                photo=InputFile(BOT_LOGO),
                caption=await locale.get_translate(lang=data['lang'], translate='select_city_error'),
                disable_notification=True
            )
        else:
            await delete_reply_message(message=message, reply_id=data['dialog_message_id'])
            reply = await message.answer_photo(
                photo=InputFile(BOT_LOGO),
                caption=await locale.get_translate(lang=data['lang'], translate='select_city_success'),
                disable_notification=True,
                reply_markup=await gen_cities_kb(cities=cities_found, lang=data['lang'])
            )
        await UserInput.Allow.set()  # Allow user input
        data['dialog_message_id'] = reply.message_id
        await database.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])


async def another_city(call: CallbackQuery, state: FSMContext) -> None:
    """
    Returns to the input of the city name

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    await call.answer(cache_time=1)
    async with state.proxy() as data:
        await delete_reply_call(call=call, reply_id=data['dialog_message_id'])
        reply = await call.bot.send_photo(
            chat_id=data['id'],
            photo=InputFile(BOT_LOGO),
            caption=await locale.get_translate(lang=data['lang'], translate='start'),
            disable_notification=True,
        )
        data['dialog_message_id'] = reply.message_id
        await database.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])


async def choice_units(call: CallbackQuery, state: FSMContext) -> None:
    """
    Processes the coordinates of the selected user city and displays a dialog to select the temperature units

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    await UserInput.previous()  # Prevent user input
    await call.answer(cache_time=1)
    async with state.proxy() as data:
        await delete_reply_call(call=call, reply_id=data['dialog_message_id'])
        reply = await call.bot.send_photo(
            chat_id=data['id'],
            photo=InputFile(BOT_LOGO),
            caption=await locale.get_translate(lang=data['lang'], translate='choice_units'),
            disable_notification=True,
            reply_markup=await gen_units_kb()
        )
        latitude, longitude, city = call.data.removeprefix('city_data=').split('&')
        data['latitude'], data['longitude'], data['city'] = float(latitude), float(longitude), city
        data['dialog_message_id'] = reply.message_id
        await database.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])


async def save_settings(call: CallbackQuery, state: FSMContext) -> None:
    """
    Saves the user's weather settings in the database

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    async with state.proxy() as data:
        await delete_reply_call(call=call, reply_id=data['dialog_message_id'])
        reply = await call.bot.send_photo(
            chat_id=data['id'],
            photo=InputFile(BOT_LOGO),
            caption=await locale.get_translate(lang=data['lang'], translate='loading_data'),
            disable_notification=True
        )
        reply_id: int = reply.message_id
        data['units']: str = 'metric' if call.data.removeprefix('units=') == 'c' else 'imperial'
        await database.save_user_settings(settings=data.as_dict())
        image_path: str = await weather.get_weather_forecast(user_id=data['id'])
        reply = await call.bot.send_photo(
            chat_id=data['id'],
            photo=InputFile(image_path),
            caption=await weather.get_current_weather(user_id=data['id']),
            disable_notification=True
        )
        remove(image_path)
        await delete_reply_call(call=call, reply_id=reply_id)
        data['dialog_message_id'] = reply.message_id
        await database.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])
        text = await locale.get_translate(lang=data['lang'], translate='save_settings')
        reply = await call.bot.send_message(chat_id=data['id'], text=f'<code>{text}</code>', disable_notification=True)
        await sleep(15)
        await call.bot.delete_message(chat_id=data['id'], message_id=reply.message_id)
        await state.reset_state(with_data=True)


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
    dp.register_message_handler(select_city, content_types=['text', 'location', 'venue'], state=UserInput.Allow)
    dp.register_callback_query_handler(another_city, text='another_city', state='*')
    dp.register_callback_query_handler(choice_units, text_contains='city_data=', state='*')
    dp.register_callback_query_handler(save_settings, text_contains='units=', state='*')
    dp.register_message_handler(unprocessed, state='*', content_types=ContentTypes.ANY)
