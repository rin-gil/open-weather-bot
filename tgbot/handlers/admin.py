""" Handling messages from bot admins """

from asyncio import sleep

from aiogram import Dispatcher
from aiogram.types import InputFile, Message

from tgbot.config import BOT_LOGO
from tgbot.models.database import database
from tgbot.models.localization import locale


async def stats(message: Message) -> None:
    """
    Shows statistics for administrators

    :param message: message from the admin
    :return: None
    """
    await message.delete()
    counter: int = await database.get_api_counter_value()
    raw_text: str = await locale.get_translate(lang=message.from_user.language_code, translate='statistics')
    phrases: list[str] = raw_text.split('---')
    text = f'ℹ️ {phrases[0]}, <b>{round((counter / 1000000) * 100)} %</b> {phrases[1]}: ' \
           f'<b>{"{0:,}".format(counter).replace(",", " ")}</b> {phrases[2]} <b>1 000 000</b>'
    answer: Message = await message.bot.send_photo(chat_id=message.from_user.id,
                                                   photo=InputFile(BOT_LOGO), caption=text)
    await sleep(10)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=answer.message_id)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(stats, commands='stats', state='*', is_admin=True)
