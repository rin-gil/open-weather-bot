""" Launches the bot """

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.misc.commands import set_default_commands
from tgbot.misc.logging import logger
from tgbot.models.database import database
from tgbot.models.localization import locale


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp: Dispatcher):
    register_admin(dp)
    register_user(dp)


async def main() -> None:
    """ Launches the bot """
    logger.info('Starting bot')

    config = load_config()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())
    bot['config'] = config

    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        locale.init()
        await database.init()
        await set_default_commands(dp)
        await dp.skip_updates()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped!')
