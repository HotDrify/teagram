from typing import KT, VT, Union

from lightdb import LightDB
from pyrogram import Client, types

from . import CloudDatabase


class Database(LightDB):
    """Локальная база данных в файле"""

    def __init__(self, location: str):
        super().__init__(location)
        self.cloud = None

    def init_cloud(self, app: Client, me: types.User):
        """Инициализация облачной базы данных"""
        self.cloud = CloudDatabase(app, me)

    def __repr__(self):
        return object.__repr__(self)

    def set(self, name: str, key: KT, value: VT):
        self.setdefault(name, {})[key] = value
        return self.save()

    def get(self, name: str, key: KT, default: VT = None):
        try:
            return self[name][key]
        except KeyError:
            return default

    def pop(self, name: str, key: KT = None, default: VT = None):
        if not key:
            value = self.pop(name, default)
        else:
            try:
                value = self[name].pop(key, default)
            except KeyError:
                value = default

        self.save()
        return value

    # async def save_data(self, message: Union[types.Message, str]):
    #     """Сохранить данные в чат"""
    #     return await self.cloud.save_data(message)

    # async def get_data(self, message_id: int):
    #     """Найти данные по айди сообщения"""
    #     return await self.cloud.get_data(message_id)
