""" Configuration settings for the bot """

import logging

from dataclasses import dataclass
from os import path
from pathlib import Path
from environs import Env

BASE_DIR: Path = Path(__file__).resolve().parent
DB_NAME: str = path.join(BASE_DIR, 'db.sqlite3')
LANGUAGES_DIR: str = path.join(BASE_DIR, 'lang')
BOT_LOGO = path.join(BASE_DIR, 'assets/bot_logo.png')
OPEN_WEATHER_LOGO = path.join(BASE_DIR, 'assets/openweather-logo.png')
LOG_FILE: str = path.join(BASE_DIR, 'OpenWeatherBot.log')

logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename=LOG_FILE,
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
)


@dataclass
class TgBot:
    token: str
    admin_ids: tuple[int]


@dataclass
class WeatherAPI:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    weather_api: WeatherAPI


def load_config() -> Config:
    """
    Loads tokens from environment variables

    :return: object of class Config
    """
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env.str('BOT_TOKEN'),
            admin_ids=tuple(map(int, env.list("ADMINS")))
        ),
        weather_api=WeatherAPI(
            token=env.str('WEATHER_API_TOKEN')
        )
    )
