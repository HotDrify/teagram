from asyncio import sleep

from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQuery,
                            InlineQueryResultArticle, InputTextMessageContent
                            )
from telethon import types

from .. import (  # ".." - т.к. модули находятся в папке teagram/modules, то нам нужно на уровень выше
    loader, utils, validators)
from ..types import Config, ConfigValue

import json
from ..__init__ import __version__
from ..utils import BASE_PATH
import atexit
import logging

data = {}

async def get_token():
    with open(f'{BASE_PATH}/db.json', 'r') as file:
        json_data = json.load(file)
    try:
        json_data.get("teagram.bot", {}).get("token", "")
    except Exception:
        return False
    else:
        return True

def get_token_sync():
    with open(f'{BASE_PATH}/db.json', 'r') as file:
        json_data = json.load(file)
    try:
        json_data.get("teagram.bot", {}).get("token", "")
    except Exception:
        return False
    else:
        return True

async def check_fork():
    pass

@loader.module(name="Dump", author="teagram", version=1)
class DumpMod(loader.Module):
    """Описание модуля"""

    def __init__(self):
        self.config = Config(
            ConfigValue(
                option='backupInterval',
                doc='⌛ Время, по истечении которого будет создана резервная копия (в секундах)',
                default=86400,
                value=self.db.get('None', 'none', 86400),
                validator=validators.Integer(minimum=43200, maximum=259200)
            )
        )

    @loader.loop(5,autostart=True)
    async def dumploop(self):
        global data

        modules = list(map(lambda x: x.name,sorted(self.manager.modules, key=lambda mod: len(str(mod)))))

        result = {
            "teagram.token": {
                "token": await get_token()
            },
            "teagram.modules": {
                "modules": modules
            },
            "teagram.version": {
                "version":  __version__
            },
            "teagram.platform": {
                "platform": utils.get_platform()
            }
        }

        data = result   

        

    async def dump_cmd(self, message: types.Message, args: str):
        modules = list(map(lambda x: x.name,sorted(self.manager.modules, key=lambda mod: len(str(mod)))))

        result = {
            "teagram.token": {
                "token": await get_token()
            },
            "teagram.modules": {
                "modules": modules
            },
            "teagram.version": {
                "version":  __version__
            },
            "teagram.platform": {
                "platform": utils.get_platform()
            }
        }

        with open(f'{BASE_PATH}/dump.json','w') as f:
            json.dump(result,f,indent=4)
        file = await self.client.upload_file(f'{BASE_PATH}/dump.json')
        await self.client.send_file(message.chat_id,file,reply_to=message.id,caption="Dump created")

        await message.delete()
    
    @atexit.register
    def create_dump():
        global data

        with open(f'{BASE_PATH}/dump.json','w') as f:
            json.dump(data, f,indent=4)

        logging.info(f"Dump file created, {BASE_PATH}/dump.json")

