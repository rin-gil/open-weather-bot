""" Handling messages from bot users """

from os import remove

from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile, Message
from aiogram.utils.exceptions import MessageIdentifierNotSpecified, MessageToDeleteNotFound

from tgbot.config import db, locale, load_config, OPEN_WEATHER_LOGO
from tgbot.keyboards.inline import gen_admin_kb, gen_cities_kb, gen_units_kb
from tgbot.misc.states import UserInput
from tgbot.services.weather_api import get_list_cities, get_weather_forecast_data, get_current_weather_data

_ADMINS: tuple[int] = load_config().tg_bot.admin_ids


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
            old_dialog_message_id=await db.get_dialog_message_id(user_id=data['id']),
            message_text=await locale.get_translate(lang=data['lang'], translation='start')
        )
    await UserInput.EnterCityName.set()  # Allow user input of text
    await db.save_dialog_message_id(user_id=data['id'], dialog_message_id=data['dialog_message_id'])


async def about(message: Message) -> None:
    """
    Handles command /about from the user

    :param message: message from the user
    :return: None
    """
    await message.delete()
    about_message = await message.bot.send_photo(
        chat_id=message.from_user.id,
        photo=InputFile(OPEN_WEATHER_LOGO),
        caption='Weather data provided by <a href="https://openweathermap.org/">OpenWeather</a>'
    )
    await sleep(10)
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
        old_dialog_message_id=await db.get_dialog_message_id(user_id=message.from_user.id),
        message_text=await locale.get_translate(lang=message.from_user.language_code, translation='stop'))
    await db.delete_user(user_id=message.from_user.id)
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
            text=await locale.get_translate(lang=data['lang'], translation='select_city'),
            chat_id=data['id'],
            message_id=data['dialog_message_id']
        )
        cities_found: list[dict[str, str]] = await get_list_cities(city_name=message.text,
                                                                   user_language_code=data['lang'])
        if len(cities_found) == 0:
            await message.bot.edit_message_text(
                text=await locale.get_translate(lang=data['lang'], translation='select_city_error'),
                chat_id=data['id'],
                message_id=data['dialog_message_id']
            )
            await UserInput.EnterCityName.set()  # Allow user input of text
        else:
            await message.bot.edit_message_text(
                text=await locale.get_translate(lang=data['lang'], translation='select_city_success'),
                chat_id=data['id'],
                message_id=data['dialog_message_id'],
                reply_markup=await gen_cities_kb(cities=cities_found, lang=data['lang'])
            )


async def back_to_input_city_name(call: CallbackQuery) -> None:
    """
    Returns to the input of the city name

    :param call: CallbackQuery
    :return: None
    """
    await call.answer(cache_time=1)
    await call.bot.edit_message_text(
        text=await locale.get_translate(lang=call.from_user.language_code, translation='start'),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    await UserInput.EnterCityName.set()  # Allow user input of text


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
            text=await locale.get_translate(lang=call.from_user.language_code, translation='choice_units'),
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
    await call.answer(text=await locale.get_translate(lang=call.from_user.language_code, translation='save_settings'),
                      show_alert=True,
                      cache_time=1)

    async with state.proxy() as data:
        data['units']: str = 'metric' if call.data.removeprefix('units=') == 'c' else 'imperial'
        await db.save_user_settings(settings=data.as_dict())
        await call.bot.edit_message_text(
            text=await locale.get_translate(lang=call.from_user.language_code, translation='loading_data'),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        path_to_forecast_image: str = await get_weather_forecast_data(user_id=call.message.chat.id)
        new_dialog_message: Message = await call.bot.send_photo(
            chat_id=call.message.chat.id,
            photo=InputFile(path_to_forecast_image),
            caption=await get_current_weather_data(user_id=call.message.chat.id),
            reply_markup=await gen_admin_kb(lang=call.from_user.language_code) if call.message.chat.id in _ADMINS else None
        )
        remove(path_to_forecast_image)
        await call.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await db.save_dialog_message_id(user_id=call.message.chat.id, dialog_message_id=new_dialog_message.message_id)
        data.clear()


async def admin_statistics(call: CallbackQuery) -> None:
    """
    Displays information about the number of requests made to OpenWeatherMap API since the beginning of the month

    :param call: CallbackQuery
    :return: None
    """
    request_counter: int = await db.get_api_counter_value()
    dialog_admin_statistics_message: str = await locale.get_translate(lang=call.from_user.language_code,
                                                                      translation='admin_statistics')
    phrases: list = dialog_admin_statistics_message.split('---')
    text = f'\u2139 {phrases[0]}\n' \
           f'{round((request_counter / 1000000) * 100)}% {phrases[1]}\n' \
           f'{"{0:,}".format(request_counter).replace(",", " ")} {phrases[2]} 1 000 000'
    await call.answer(text=text, show_alert=True, cache_time=1)


async def unprocessed(message: Message) -> None:
    """
    Deletes unprocessed messages or commands from the user

    :param message: message from the user
    :return: None
    """
    await message.delete()


def register_handlers(dp: Dispatcher) -> None:
    """
    Registers the handling of commands from the user in the Dispatcher.

    :param dp: Dispatcher
    :return: None
    """
    pass
    dp.register_message_handler(start, commands='start', state='*')
    dp.register_message_handler(about, commands='about', state='*')
    dp.register_message_handler(stop, commands='stop', state='*')
    dp.register_message_handler(select_city, state=UserInput.EnterCityName)
    dp.register_callback_query_handler(back_to_input_city_name, text='another_city')
    dp.register_callback_query_handler(choice_units, text_contains='city_data=')
    dp.register_callback_query_handler(save_settings, text_contains='units=')
    dp.register_callback_query_handler(admin_statistics, text='admin')
    dp.register_message_handler(unprocessed, state='*', content_types=types.ContentTypes.ANY)
