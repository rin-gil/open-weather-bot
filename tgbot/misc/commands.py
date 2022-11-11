""" Sets commands for the bot """

from aiogram import Dispatcher
from aiogram.types import BotCommand

from tgbot.models.localization import locale


async def set_default_commands(dp: Dispatcher) -> None:
    """ Sets commands for the bot """
    for lang in await locale.get_list_languages():
        await dp.bot.set_my_commands(
            commands=[BotCommand('start', await locale.get_translate(lang=lang, translate='command_start')),
                      BotCommand('about', await locale.get_translate(lang=lang, translate='command_about')),
                      BotCommand('stop', await locale.get_translate(lang=lang, translate='command_stop'))],
            language_code=lang
        )
