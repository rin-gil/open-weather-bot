"""Configuration settings for the bot"""

from os.path import join, normpath
from pathlib import Path
from typing import NamedTuple

from environs import Env


BASE_DIR: Path = Path(__file__).resolve().parent.parent
BOT_LOGO: str = normpath(join(BASE_DIR, "tgbot/assets/logo/bot_logo.png"))
DB_FILE: str = normpath(join(BASE_DIR, "tgbot/db.sqlite3"))
LOCALES_DIR: str = normpath(join(BASE_DIR, "tgbot/locales"))
LOG_FILE: str = join(BASE_DIR, "open-weather-bot.log")


class TgBot(NamedTuple):
    """Bot token"""

    token: str
    admin_ids: tuple[int, ...]


class WeatherToken(NamedTuple):
    """Weather API token"""

    token: str


class Config(NamedTuple):
    """Bot config"""

    tg_bot: TgBot
    weather_api: WeatherToken


def load_config() -> Config:
    """Loads data from environment variables"""
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(token=env.str("BOT_TOKEN"), admin_ids=tuple(map(int, env.list("ADMINS")))),
        weather_api=WeatherToken(token=env.str("WEATHER_API_TOKEN")),
    )
