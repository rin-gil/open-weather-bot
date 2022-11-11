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
    api_counter: int = await database.get_api_counter_value()
    users_counter: int = await database.get_users_counter()
    raw_text: str = await locale.get_translate(lang=message.from_user.language_code, translate='statistics')
    phrases: list[str] = raw_text.split('---')
    text = f'ℹ️ <b>{phrases[0]}:</b>\n\n' \
           f'\u2022 {phrases[1]},\n' \
           f'  <b>{round((api_counter / 1000000) * 100)} %</b> {phrases[2]}:\n' \
           f'  <b>{"{0:,}".format(api_counter).replace(",", " ")}</b> {phrases[3]} <b>1 000 000</b>\n\n' \
           f'\u2022 {phrases[4]}: <b>{users_counter}</b>'
    answer: Message = await message.bot.send_photo(chat_id=message.from_user.id,
                                                   photo=InputFile(BOT_LOGO), caption=text)
    await sleep(10)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=answer.message_id)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(stats, commands='stats', state='*', is_admin=True)
