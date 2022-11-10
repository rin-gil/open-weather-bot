""" Configuration settings for the bot """

from dataclasses import dataclass
from os.path import join
from pathlib import Path

from environs import Env


BASE_DIR: Path = Path(__file__).resolve().parent
BOT_LOGO: str = join(BASE_DIR, 'assets/logo/bot_logo.png')


@dataclass
class TgBot:
    token: str
    admin_ids: tuple[int]


@dataclass
class WeatherToken:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    weather_api: WeatherToken


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
            admin_ids=tuple(map(int, env.list('ADMINS')))
        ),
        weather_api=WeatherToken(
            token=env.str('WEATHER_API_TOKEN')
        )
    )
