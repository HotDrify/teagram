from typing import KT, VT, Union

from lightdb import LightDB
from telethon import TelegramClient, types

from . import CloudDatabase


class Database(LightDB):
    """Local database"""

    def __init__(self, location: str):
        super().__init__(location)
        self.cloud = None

    def init_cloud(self, app: TelegramClient, me: types.User):
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