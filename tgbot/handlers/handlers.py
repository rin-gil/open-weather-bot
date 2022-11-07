""" Handling messages from bot users """

from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageIdentifierNotSpecified

from tgbot.config import load_config, OPEN_WEATHER_LOGO
from tgbot.keyboards.inline import generate_cities_keyboard, generate_temperature_units_keyboard, \
    generate_admin_keyboard
from tgbot.misc.locale import get_dialog_message_answer
from tgbot.misc.states import TextInput
from tgbot.models.db import get_dialog_message_id, save_dialog_message_id, delete_user_from_db, \
    save_user_weather_settings, get_current_api_counter_value
from tgbot.services.weather_api import get_list_cities, get_weather_forecast_data, get_current_weather_data

ADMINS: tuple[int] = load_config().tg_bot.admin_ids


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


async def dialog_command_start(message: Message, state: FSMContext) -> None:
    """
    Handles command /start from the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await message.delete()
    await state.reset_state()
    async with state.proxy() as data:
        data['user_id']: int = message.from_user.id
        data['user_language']: str = message.from_user.language_code
        data['dialog_message_id']: int = await _del_old_dialog_message_and_send_new(
            message=message,
            old_dialog_message_id=await get_dialog_message_id(user_id=data['user_id']),
            message_text=await get_dialog_message_answer(user_language_code=data['user_language'],
                                                         dialog_message_name='dialog_command_start')
        )
    await TextInput.EnterCityName.set()  # Allow user input of text
    await save_dialog_message_id(user_id=data['user_id'], dialog_message_id=data['dialog_message_id'])


async def dialog_command_about(message: Message) -> None:
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


async def dialog_command_stop(message: Message, state: FSMContext) -> None:
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
        old_dialog_message_id=await get_dialog_message_id(user_id=message.from_user.id),
        message_text=await get_dialog_message_answer(user_language_code=message.from_user.language_code,
                                                     dialog_message_name='dialog_command_stop'))
    await delete_user_from_db(user_id=message.from_user.id)
    await sleep(5)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=dialog_message_id)


async def dialog_message_select_city(message: types.Message, state: FSMContext) -> None:
    """
    Processing the result of the search of the city entered by the user

    :param message: message from the user
    :param state: state from Final State Machine
    :return: None
    """
    await message.delete()
    await TextInput.previous()  # Deny user input (prevents repeated city search if OpenWeatherMap API service
    #                             takes a long time to process the request)
    async with state.proxy() as data:
        await message.bot.edit_message_text(
            text=await get_dialog_message_answer(user_language_code=data['user_language'],
                                                 dialog_message_name='dialog_message_select_city'),
            chat_id=data['user_id'],
            message_id=data['dialog_message_id']
        )
        cities_found: list = await get_list_cities(city_name=message.text, user_language_code=data['user_language'])
        if len(cities_found) == 0:
            await message.bot.edit_message_text(
                text=await get_dialog_message_answer(user_language_code=data['user_language'],
                                                     dialog_message_name='dialog_message_select_city_error'),
                chat_id=data['user_id'],
                message_id=data['dialog_message_id']
            )
            await TextInput.EnterCityName.set()  # Allow user input of text
        else:
            await message.bot.edit_message_text(
                text=await get_dialog_message_answer(user_language_code=data['user_language'],
                                                     dialog_message_name='dialog_message_select_city_success'),
                chat_id=data['user_id'],
                message_id=data['dialog_message_id'],
                reply_markup=await generate_cities_keyboard(cities=cities_found,
                                                            user_language_code=data['user_language'])
            )


async def back_to_input_city_name(call: CallbackQuery) -> None:
    """
    Returns to the input of the city name

    :param call: CallbackQuery
    :return: None
    """
    await call.answer(cache_time=1)
    await call.bot.edit_message_text(
        text=await get_dialog_message_answer(user_language_code=call.from_user.language_code,
                                             dialog_message_name='dialog_command_start'),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    await TextInput.EnterCityName.set()  # Allow user input of text


async def dialog_choice_of_temperature_units(call: CallbackQuery, state: FSMContext) -> None:
    """
    Processes the coordinates of the selected user city and displays a dialog to select the temperature units

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    await call.answer(cache_time=1)
    async with state.proxy() as data:
        city_data: str = call.data.removeprefix('city_coords_and_name=')
        data['city_latitude'], data['city_longitude'], data['city_local_name'] = city_data.split('&')
        await call.bot.edit_message_text(
            text=await get_dialog_message_answer(user_language_code=call.from_user.language_code,
                                                 dialog_message_name='dialog_choice_of_temperature_units'),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=await generate_temperature_units_keyboard()
        )


async def dialog_save_weather_settings(call: CallbackQuery, state: FSMContext) -> None:
    """
    Saves the user's weather settings in the database

    :param call: CallbackQuery
    :param state: state from Final State Machine
    :return: None
    """
    await call.answer(text=await get_dialog_message_answer(user_language_code=call.from_user.language_code,
                                                           dialog_message_name='dialog_save_weather_settings'),
                      show_alert=True,
                      cache_time=1)

    async with state.proxy() as data:
        data['temperature_units']: str = 'metric' if call.data.removeprefix('temperature_units=') == 'c' else 'imperial'
        await save_user_weather_settings(data=data.as_dict())
        await call.bot.edit_message_text(
            text=await get_dialog_message_answer(user_language_code=call.from_user.language_code,
                                                 dialog_message_name='dialog_loading_weather_data'),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        new_dialog_message: Message = await call.bot.send_photo(
            chat_id=call.message.chat.id,
            photo=await get_weather_forecast_data(user_id=call.message.chat.id),
            caption=await get_current_weather_data(user_id=call.message.chat.id),
            reply_markup=await generate_admin_keyboard(
                user_language_code=call.from_user.language_code
            ) if call.message.chat.id in ADMINS else None
        )
        await call.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await save_dialog_message_id(user_id=call.message.chat.id, dialog_message_id=new_dialog_message.message_id)
        data.clear()


async def dialog_admin_statistics(call: CallbackQuery) -> None:
    """
    Displays information about the number of requests made to OpenWeatherMap API since the beginning of the month

    :param call: CallbackQuery
    :return: None
    """
    request_counter: int = await get_current_api_counter_value()
    dialog_admin_statistics_message: str = await get_dialog_message_answer(
        user_language_code=call.from_user.language_code,
        dialog_message_name='dialog_admin_statistics'
    )
    phrases: list = dialog_admin_statistics_message.split('---')
    text = f'ℹ {phrases[0]}\n' \
           f'{round((request_counter / 1000000) * 100)}% {phrases[1]}\n' \
           f'{"{0:,}".format(request_counter).replace(",", " ")} {phrases[2]} 1 000 000'
    await call.answer(text=text, show_alert=True, cache_time=1)


async def dialog_unprocessed(message: Message) -> None:
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
    dp.register_message_handler(dialog_command_start, commands='start', state='*')
    dp.register_message_handler(dialog_command_about, commands='about', state='*')
    dp.register_message_handler(dialog_command_stop, commands='stop', state='*')
    dp.register_message_handler(dialog_message_select_city, state=TextInput.EnterCityName)
    dp.register_callback_query_handler(back_to_input_city_name, text='input_another_city')
    dp.register_callback_query_handler(dialog_choice_of_temperature_units, text_contains='city_coords_and_name=')
    dp.register_callback_query_handler(dialog_save_weather_settings, text_contains='temperature_units=')
    dp.register_callback_query_handler(dialog_admin_statistics, text='admin_keyboard')
    dp.register_message_handler(dialog_unprocessed, state='*', content_types=types.ContentTypes.ANY)
