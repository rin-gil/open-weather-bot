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
            dialog_message_id INTEGER,
            language_code VARCHAR(2),
            city_latitude VARCHAR(11),
            city_longitude VARCHAR(11),
            temperature_units VARCHAR(8)
            );"""
        )


async def get_dialog_message_id(user_id: int) -> int:
    """
    Returns the id of the dialog message with the user

    :param user_id: user id
    :return: dialog message id
    """
    async with connect(database=DB_NAME) as db:
        value: tuple = (user_id, )
        dialog_message_id: int = 0
        async with db.execute("""SELECT dialog_message_id FROM users WHERE user_id=?;""", value) as cursor:
            async for row in cursor:
                dialog_message_id = row[0]
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
        await db.execute(
            """INSERT INTO users (user_id, dialog_message_id) VALUES (?, ?)
            ON CONFLICT (user_id) DO UPDATE SET dialog_message_id=excluded.dialog_message_id""", values
        )
        await db.commit()
