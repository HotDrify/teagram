from telethon import types

from .. import loader, utils

from ..__init__ import __version__
from ..utils import BASE_PATH

import atexit
import logging
import json

data = {}

logger = logging.getLogger()

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

@loader.module(name="Dump", author="teagram")
class DumpMod(loader.Module):
    """Makes dump with information"""

    @loader.loop(5, autostart=True)
    async def dumploop(self):
        global data

        modules = [mod.name for mod in self.manager.modules]

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

        

    async def dump_cmd(self, message: types.Message):
        modules = [mod.name for mod in self.manager.modules]

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
            json.dump(result, f, indent=4)

        file = await self.client.upload_file(f'{BASE_PATH}/dump.json')
        await self.client.send_file(
            message.chat_id,
            file,
            reply_to=message.id,
            caption="Dump created"
        )

        await message.delete()
    
    @atexit.register
    def create_dump():
        global data

        with open(f'{BASE_PATH}/dump.json','w') as f:
            json.dump(data, f, indent=4)

        logger.info(f"Dump file created, {BASE_PATH}/dump.json")

