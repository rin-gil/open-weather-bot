""" Model describing the work with the database """

from datetime import datetime
from os.path import join
from typing import NamedTuple

from aiosqlite import connect

from tgbot.config import BASE_DIR
from tgbot.misc.logging import logger


class UserWeatherSettings(NamedTuple):
    """ A class that describes the user's weather settings """
    id: int
    dialog_message_id: int
    lang: str
    city: str
    latitude: float
    longitude: float
    units: str


class Database:
    """ A class for working with the database """

    def __init__(self, path: str) -> None:
        """
        Defines the path to the database file

        :param path: path to the database file
        """
        self._db_path = path

    async def init(self) -> None:
        """ Creates a database file and a table in it """
        try:
            async with connect(database=self._db_path) as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY ON CONFLICT IGNORE,
                        dialog_message_id INTEGER NOT NULL,
                        lang VARCHAR(2) DEFAULT NULL,
                        city VARCHAR(72) DEFAULT NULL,
                        latitude REAL DEFAULT NULL,
                        longitude REAL DEFAULT NULL,
                        units VARCHAR(8) DEFAULT NULL
                    );
                    """
                )
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS api_request_counters (
                            month VARCHAR(7) PRIMARY KEY,
                            counter INTEGER NOT NULL DEFAULT 0
                            );
                    """
                )
        except Exception as ex:
            logger.critical('Database connection error: %s', ex)
            logger.info('Bot stopped!')
            exit()

    async def get_dialog_message_id(self, user_id: int) -> int:
        """
        Returns the identifier of the dialog message with the user from the database

        :param user_id: user id
        :return: dialog message id
        """
        async with connect(database=self._db_path) as db:
            dialog_message_id: int = 0
            async with db.execute("""SELECT dialog_message_id FROM users WHERE id=?;""", (user_id,)) as cursor:
                async for row in cursor:
                    dialog_message_id: int = row[0]
            return dialog_message_id

    async def save_dialog_message_id(self, user_id: int, dialog_message_id: int) -> None:
        """
        Saves the identifier of the dialog message with the user in the database

        :param user_id: user id
        :param dialog_message_id: dialog message id
        :return: None
        """
        async with connect(database=self._db_path) as db:
            await db.execute(
                """
                INSERT INTO users (id, dialog_message_id) VALUES (?, ?)
                ON CONFLICT (id) DO UPDATE SET dialog_message_id=excluded.dialog_message_id;
                """, (user_id, dialog_message_id)
            )
            await db.commit()

    async def get_user_settings(self, user_id: int) -> UserWeatherSettings:
        """
        Returns the user's weather settings

        :param user_id: user id
        :return: user weather settings
        """
        async with connect(database=self._db_path) as db:
            async with db.execute("""SELECT * FROM users WHERE id=?""", (user_id,)) as cursor:
                async for row in cursor:
                    return UserWeatherSettings(
                        id=row[0],
                        dialog_message_id=row[1],
                        lang=row[2],
                        city=row[3],
                        latitude=row[4],
                        longitude=row[5],
                        units=row[6]
                    )

    async def save_user_settings(self, settings: dict) -> None:
        """
        Saves the user's weather settings in the database

        :param settings: user weather settings
        :return: None
        """
        async with connect(database=self._db_path) as db:
            await db.execute(
                """
                UPDATE users
                SET dialog_message_id=?,
                    lang=?,
                    city=?,
                    latitude=?,
                    longitude=?,
                    units=?
                WHERE id=?;
                """, (
                    settings.get('dialog_message_id'),
                    settings.get('lang'),
                    settings.get('city'),
                    settings.get('latitude'),
                    settings.get('longitude'),
                    settings.get('units'),
                    settings.get('id')
                )
            )
            await db.commit()

    async def get_all_users(self) -> list[UserWeatherSettings]:
        """
        Returns the settings of all users

        :return: users weather settings
        """
        users: list[UserWeatherSettings] = []
        async with connect(database=self._db_path) as db:
            async with db.execute("""SELECT * FROM users""") as cursor:
                async for row in cursor:
                    users.append(
                        UserWeatherSettings(
                            id=row[0],
                            dialog_message_id=row[1],
                            lang=row[2],
                            city=row[3],
                            latitude=row[4],
                            longitude=row[5],
                            units=row[6]
                        )
                    )
        return users

    async def get_users_counter(self) -> int:
        """
        Returns the count of users in the database

        :return: count of users
        """
        async with connect(database=self._db_path) as db:
            async with db.execute("""SELECT COUNT() FROM users""") as cursor:
                async for row in cursor:
                    return row[0]

    async def delete_user(self, user_id: int) -> None:
        """
        Deletes a user from the database

        :param user_id: user id
        :return: None
        """
        async with connect(database=self._db_path) as db:
            await db.execute("""DELETE FROM users WHERE id=?;""", (user_id,))
            await db.commit()

    async def get_api_counter_value(self) -> int:
        """
        Returns the number of requests to OpenWeatherAPI made since the beginning of the month

        :return: number of requests to OpenWeatherAPI
        """
        async with connect(database=self._db_path) as db:
            async with db.execute(
                    """
                    SELECT counter FROM api_request_counters WHERE month=?;
                    """, (datetime.now().strftime('%Y.%m'),)
            ) as cursor:
                async for row in cursor:
                    return row[0]

    async def increase_api_counter(self) -> None:
        """
        Increases OpenWeatherMap API request counter value

        :return: None
        """
        async with connect(database=self._db_path) as db:
            await db.execute(
                """
                INSERT INTO api_request_counters (month, counter) VALUES (?, ?)
                ON CONFLICT (month) DO UPDATE SET counter=counter+1;
                """, (datetime.now().strftime('%Y.%m'), 1)
            )
            await db.commit()


database: Database = Database(path=join(BASE_DIR, 'db.sqlite3'))
