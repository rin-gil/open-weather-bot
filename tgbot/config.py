import logging

from dataclasses import dataclass
from environs import Env
from os import path
from pathlib import Path


BANNED_CONTENT: tuple = ('animation', 'audio', 'contact', 'document', 'game', 'location', 'photo',
                         'pinned_message', 'poll', 'sticker', 'video', 'video_note', 'voice')

BASE_DIR: Path = Path(__file__).resolve().parent
LANGUAGES_DIR: str = path.join(BASE_DIR, 'lang')
LOG_FILE: str = path.join(BASE_DIR, 'OpenWeatherBot.log')

logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename=LOG_FILE,
    level=logging.INFO,
    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)


@dataclass
class TgBot:
    token: str


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
        ),
        misc=Miscellaneous()
    )
