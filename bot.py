from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from tgbot.config import db, load_config, locale, logger
from tgbot.handlers.handlers import register_handlers


bot: Bot = Bot(token=load_config().tg_bot.token, parse_mode='HTML')
dp: Dispatcher = Dispatcher(bot=bot, storage=MemoryStorage())


async def on_startup(_):
    register_handlers(dp)
    await db.db_init()
    locale.init()


async def on_shutdown(_):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()


def main() -> None:
    """
    Launches the bot

    :return: None
    """
    logger.info('Starting bot')
    executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped!')
