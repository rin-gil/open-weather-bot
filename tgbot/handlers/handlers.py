from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from tgbot.misc.locale import get_bot_message
from tgbot.misc.states import TextInput


async def command_start(message: Message, state: FSMContext) -> None:
    """
    Handles command /start from the user.

    :param message: Message from the user
    :param state: State from FSM
    :return: None
    """
    await message.delete()
    async with state.proxy() as data:
        language_code: str = message.from_user.language_code
        bot_message: Message = await message.answer(text=get_bot_message(language_code=language_code,
                                                                         bot_message='command_start'))
        data['user_id'] = message.from_user.id
        data['user_language'] = language_code
        data['bot_message_id'] = bot_message.message_id
        await TextInput.Unlock.set()


async def command_help(message: Message) -> None:
    """
    Handles command /help from the user.

    :param message: Message from the user
    :return: None
    """
    await message.delete()
    await message.answer(text=get_bot_message(language_code=message.from_user.language_code,
                                              bot_message='command_help'))


async def command_stop(message: Message) -> None:
    """
    Handles command /help from the user.

    :param message: Message from the user
    :return: None
    """
    await message.delete()
    await message.answer(text=get_bot_message(language_code=message.from_user.language_code,
                                              bot_message='command_stop'))
    # TODO добавить удаление пользователя из БД


async def unknown_commands(message: Message) -> None:
    """
    Handles unknown commands.

    :param message: Message from the user
    :return: None
    """
    await message.delete()


def register_commands(dp: Dispatcher) -> None:
    """
    Registers the handling of commands from the user in the Dispatcher.

    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(command_start, commands='start')
    dp.register_message_handler(command_help, commands='help')
    dp.register_message_handler(command_stop, commands='stop')
    dp.register_message_handler(unknown_commands, Text(startswith='/'), state="*", content_types=types.ContentTypes.ANY)
