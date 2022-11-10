""" Sets commands for the bot """

from aiogram import Dispatcher
from aiogram.types import BotCommand


async def set_default_commands(dp: Dispatcher) -> None:
    """ Sets commands for the bot """
    await dp.bot.set_my_commands(
        [
            BotCommand('start', '▶️ Run the bot'),
            BotCommand('about', 'ℹ️ Bot info'),
            BotCommand('stop', '⏹ Stop bot and delete data')
        ]
    )
