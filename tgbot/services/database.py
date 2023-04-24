""" Model describing the work with the database """

from datetime import datetime
from sqlite3 import OperationalError
from sys import exit as sys_exit

from aiosqlite import connect

from tgbot.config import DB_FILE
from tgbot.misc.logger import logger
from tgbot.services.classes import User, UserWeatherSettings


class Database:
    """A class for working with the database"""

    def __init__(self, path: str) -> None:
        """Defines the path to the database file"""
        self._db_path = path

    async def init(self) -> None:
        """Creates a database file and a table in it"""
        try:
            async with connect(database=self._db_path) as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY ON CONFLICT IGNORE,
                        dialog_id INTEGER NOT NULL,
                        lang VARCHAR(2),
                        city VARCHAR(72),
                        latitude REAL,
                        longitude REAL,
                        units VARCHAR(8)
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
        except OperationalError as ex:
            logger.critical("Database connection error: %s", ex)
            sys_exit()

    async def save_dialog_id(self, user_id: int, dialog_id: int) -> None:
        """Saves the identifier of the dialog message with the user in the database"""
        async with connect(database=self._db_path) as db:
            await db.execute(
                """
                INSERT INTO users (id, dialog_id) VALUES (?, ?)
                ON CONFLICT (id) DO UPDATE SET dialog_id=excluded.dialog_id;
                """,
                (user_id, dialog_id),
            )
            await db.commit()

    async def save_city_coords(self, user_id: int, city: str, latitude: float, longitude: float) -> None:
        """Saves the coordinates of the selected city in the database"""
        async with connect(database=self._db_path) as db:
            await db.execute(
                """UPDATE users SET city=?, latitude=?, longitude=? WHERE id=?;""", (city, latitude, longitude, user_id)
            )
            await db.commit()

    async def save_user_settings(self, user_id: int, lang_code: str, measure_units: str) -> None:
        """Saves the user's weather settings in the database"""
        async with connect(database=self._db_path) as db:
            await db.execute("""UPDATE users SET lang=?, units=? WHERE id=?;""", (lang_code, measure_units, user_id))
            await db.commit()

    async def get_dialog_id_if_exists(self, user_id: int) -> int | None:
        """Returns the id of the dialog message with the user from the database"""
        dialog_id: int | None = None
        async with connect(database=self._db_path) as db:
            async with db.execute("""SELECT dialog_id FROM users WHERE id=?;""", (user_id,)) as cursor:
                async for row in cursor:
                    dialog_id = row[0]
        return dialog_id

    async def get_user_settings(self, user_id: int) -> UserWeatherSettings:
        """Returns the user's weather settings"""
        async with connect(database=self._db_path) as db:
            async with db.execute(
                """SELECT lang, city, latitude, longitude, units FROM users WHERE id=?;""", (user_id,)
            ) as cursor:
                async for row in cursor:
                    user_weather_settings: UserWeatherSettings = UserWeatherSettings(
                        lang=row[0], city=row[1], latitude=row[2], longitude=row[3], units=row[4]
                    )
        return user_weather_settings

    async def get_list_all_users(self) -> list[User]:
        """Returns the list of all users"""
        users: list[User] = []
        async with connect(database=self._db_path) as db:
            async with db.execute("""SELECT id, dialog_id FROM users WHERE units NOT NULL;""") as cursor:
                async for row in cursor:
                    users.append(User(id=row[0], dialog_id=row[1]))
        return users

    async def delete_user(self, user_id: int) -> None:
        """Deletes a user from the database"""
        async with connect(database=self._db_path) as db:
            await db.execute("""DELETE FROM users WHERE id=?;""", (user_id,))
            await db.commit()

    async def get_number_of_users(self) -> int:
        """Returns the number of users in the database"""
        counter: int = 0
        async with connect(database=self._db_path) as db:
            async with db.execute("""SELECT COUNT() FROM users;""") as cursor:
                async for row in cursor:
                    counter = row[0]
        return counter

    async def get_api_counter_value(self) -> int:
        """Returns the number of requests to OpenWeatherAPI made since the beginning of the month"""
        counter: int = 0
        async with connect(database=self._db_path) as db:
            async with db.execute(
                """SELECT counter FROM api_request_counters WHERE month=?;""", (datetime.now().strftime("%Y.%m"),)
            ) as cursor:
                async for row in cursor:
                    counter = row[0]
        return counter

    async def increase_api_counter(self) -> None:
        """Increases OpenWeatherMap API request counter value"""
        async with connect(database=self._db_path) as db:
            await db.execute(
                """
                INSERT INTO api_request_counters (month, counter) VALUES (?, ?)
                ON CONFLICT (month) DO UPDATE SET counter=counter+1;
                """,
                (datetime.now().strftime("%Y.%m"), 1),
            )
            await db.commit()


database: Database = Database(path=DB_FILE)
