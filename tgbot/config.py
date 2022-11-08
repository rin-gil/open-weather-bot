""" Configuration settings for the bot """

import logging

from dataclasses import dataclass
from os.path import join
from pathlib import Path

from environs import Env

from tgbot.models.localization import Localization
from tgbot.models.database import Database

BASE_DIR: Path = Path(__file__).resolve().parent

BOT_LOGO: str = join(BASE_DIR, 'assets/logo/bot_logo.png')
OPEN_WEATHER_LOGO: str = join(BASE_DIR, 'assets/logo/openweather-logo.png')

db: Database = Database(path=join(BASE_DIR, 'db.sqlite3'))
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename=path.join(BASE_DIR, 'OpenWeatherBot.log'),
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
)
locale: Localization = Localization(path=join(BASE_DIR, 'lang'), logger=logger)


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
