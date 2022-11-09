""" Allows to perform actions if the user is an administrator """

from typing import Optional

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class AdminFilter(BoundFilter):
    """ Allows to perform actions if the user is an administrator """
    key = 'is_admin'

    def __init__(self, is_admin: Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        config: Config = obj.bot.get('config')
        return (obj.from_user.id in config.tg_bot.admin_ids) == self.is_admin
