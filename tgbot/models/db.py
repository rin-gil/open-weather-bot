""" Functions for working with the database """

from datetime import datetime
from aiosqlite import connect
from tgbot.config import DB_NAME


async def db_init() -> None:
    """
    Creates a database file and a table in it

    :return: None
    """
    async with connect(database=DB_NAME) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            dialog_message_id INTEGER NOT NULL,
            language_code VARCHAR(2),
            city_local_name VARCHAR(72),
            city_latitude VARCHAR(11),
            city_longitude VARCHAR(11),
            temperature_units VARCHAR(8)
            );"""
        )
        await db.execute(
            """CREATE TABLE IF NOT EXISTS api_request_counters (
            month VARCHAR(7) PRIMARY KEY,
            counter INTEGER NOT NULL DEFAULT 0
            );"""
        )


async def get_dialog_message_id(user_id: int) -> int:
    """
    Returns the id of the dialog message with the user

    :param user_id: user id
    :return: dialog message id
    """
    async with connect(database=DB_NAME) as db:
        value: tuple = (user_id,)
        dialog_message_id: int = 0
        async with db.execute("""SELECT dialog_message_id FROM users WHERE user_id=?;""", value) as cursor:
            async for row in cursor:
                dialog_message_id: int = row[0]
        return dialog_message_id


async def save_dialog_message_id(user_id: int, dialog_message_id: int) -> None:
    """
    Saves the id of the dialog message with the user,
    if the user exists in the database, updates the id of the dialog message

    :param user_id: user id
    :param dialog_message_id: dialog_message id
    :return: None
    """
    async with connect(database=DB_NAME) as db:
        values: tuple = (user_id, dialog_message_id)
        await db.execute("""INSERT INTO users (user_id, dialog_message_id) VALUES (?, ?)
            ON CONFLICT (user_id) DO UPDATE SET dialog_message_id=excluded.dialog_message_id;""", values)
        await db.commit()


async def increase_api_counter() -> None:
    """
    Increases OpenWeatherMap API request counter value

    :return: None
    """
    async with connect(database=DB_NAME) as db:
        values: tuple = (datetime.now().strftime('%Y.%m'), 1)
        await db.execute("""INSERT INTO api_request_counters (month, counter) VALUES (?, ?)
            ON CONFLICT (month) DO UPDATE SET counter=counter+1;""", values)
        await db.commit()


async def get_current_api_counter_value() -> int:
    """
    Returns the number of requests to OpenWeatherAPI made since the beginning of the month

    :return: number of requests to OpenWeatherAPI
    """
    async with connect(database=DB_NAME) as db:
        value: tuple = (datetime.now().strftime('%Y.%m'),)
        async with db.execute("""SELECT counter FROM api_request_counters WHERE month=?;""", value) as cursor:
            async for row in cursor:
                api_counter_value: int = row[0]
        return api_counter_value


async def get_user_weather_settings(user_id: int) -> dict:
    """
    Returns the user's weather settings

    :param user_id: user id
    :return: dictionary with user weather settings
    """
    value: tuple = (user_id,)
    async with connect(database=DB_NAME) as db:
        async with db.execute("""SELECT * FROM users WHERE user_id=?""", value) as cursor:
            async for row in cursor:
                return dict(
                    {'user_id': row[0],
                     'dialog_message_id': row[1],
                     'language_code': row[2],
                     'city_local_name': row[3],
                     'city_latitude': row[4],
                     'city_longitude': row[5],
                     'temperature_unit': row[6]
                     }
                )


async def save_user_weather_settings(data: dict[str, int | str]) -> None:
    """
    Saves the id of the dialog message with the user,
    if the user exists in the database, updates the id of the dialog message

    :param data: dictionary with weather settings
    :return: None
    """
    async with connect(database=DB_NAME) as db:
        values: tuple = (
            data.get('dialog_message_id'),
            data.get('user_language'),
            data.get('city_local_name'),
            data.get('city_latitude'),
            data.get('city_longitude'),
            data.get('temperature_units'),
            data.get('user_id')
        )
        await db.execute(
            """UPDATE users
            SET dialog_message_id=?,
            language_code=?,
            city_local_name=?,
            city_latitude=?,
            city_longitude=?,
            temperature_units=?
            WHERE user_id=?;""", values
        )
        await db.commit()


async def delete_user_from_db(user_id: int) -> None:
    """
    Deletes a user from the database

    :param user_id: user id
    :return:
    """
    async with connect(database=DB_NAME) as db:
        value: tuple = (user_id,)
        await db.execute("""DELETE FROM users WHERE user_id=?;""", value)
        await db.commit()
