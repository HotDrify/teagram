from .. import loader, utils
from ..__init__ import __version__
from ..utils import BASE_PATH

import atexit
import logging
import json

PATH = f'{BASE_PATH}/dump.json'

data = {}
logger = logging.getLogger()

def get_token():
    with open(PATH, 'r') as file:
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

    strings = {'name': 'dump'}

    @loader.loop(5, autostart=True)
    async def dumploop(self):
        global data

        modules = [mod.name for mod in self.manager.modules]

        result = {
            "teagram.token": {
                "token": get_token()
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

    async def dump_cmd(self, message):
        modules = [mod.name for mod in self.manager.modules]

        result = {
            "teagram.token": {
                "token": get_token()
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

        with open(PATH, 'w') as f:
            json.dump(result, f, indent=4)

        await utils.answer(
            message,
            PATH,
            document=True,
            caption=self.strings("dumped")
        )
    
    @atexit.register
    def create_dump():
        global data

        with open(PATH,'w') as f:
            json.dump(data, f, indent=4)

        logger.info(f"Dump file created, {PATH}")

