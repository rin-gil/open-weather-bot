""" Functions for sending scheduled weather data """

from asyncio import sleep
from os import remove as os_remove

from aiogram import Dispatcher
from aiogram.types import InputFile, Message
from aiogram.utils.exceptions import BotBlocked, RetryAfter, UserDeactivated

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.models.database import database, User
from tgbot.services.weather import weather


async def update_weather_data(dp: Dispatcher) -> None:
    """Updates weather data for all users"""
    users: list[User] = await database.get_list_all_users()
    for user in users:
        weather_forecast: str = await weather.get_weather_forecast(user_id=user.id)
        current_weather: str = await weather.get_current_weather(user_id=user.id)
        try:
            dialog: Message = await dp.bot.send_photo(
                chat_id=user.id, photo=InputFile(weather_forecast), caption=current_weather, disable_notification=True
            )
            await database.save_dialog_id(user_id=user.id, dialog_id=dialog.message_id)
        except (BotBlocked, UserDeactivated):
            await database.delete_user(user_id=user.id)
        except RetryAfter as ex:
            await sleep(ex.timeout)
            dialog = await dp.bot.send_photo(
                chat_id=user.id, photo=InputFile(weather_forecast), caption=current_weather, disable_notification=True
            )
            await database.save_dialog_id(user_id=user.id, dialog_id=dialog.message_id)
        finally:
            await dp.bot.delete_message(chat_id=user.id, message_id=user.dialog_id)
            if weather_forecast[-12:-4] != "bot_logo":
                os_remove(weather_forecast)


async def schedule(dp: Dispatcher) -> None:
    """Creates a weather update task in the scheduler"""
    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=update_weather_data, trigger="cron", hour="0, 3, 6, 9, 12, 15, 18, 21", args=(dp,), timezone="UTC"
    )
    scheduler.start()
