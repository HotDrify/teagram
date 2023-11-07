from .. import loader, utils
from ..__init__ import __version__
from ..utils import BASE_PATH, BASE_DIR
import telethon

import atexit
import logging
import json
from git import Repo

PATH = f'{BASE_PATH}/dump.json'
REPO = Repo(BASE_DIR)

data = {}
logger = logging.getLogger()

def get_token():
    with open(BASE_PATH / "db.json", 'r') as file:
        json_data = json.load(file)
    try:
        if json_data["teagram.bot"]["token"]:
            return True
    except Exception:
        return False

def get_git_info(commit=False,url=False,branch=False):
    repo = REPO

    if commit:
        commit = repo.commit()
        return commit
    
    if url:
        origin = repo.remotes.origin
        origin_url = origin.url
        return origin_url
    
    if branch:
        return repo.active_branch.name
    

@loader.module(name="Dump", author="teagram")
class DumpMod(loader.Module):
    """Makes dump with information"""

    strings = {'name': 'dump'}

    def gen(self) -> dict:
        {
            "teagram.token": {
                "token": get_token()
            },
            "teagram.modules": {
                "modules": [mod.name for mod in self.manager.modules]
            },
            "teagram.version": {
                "version":  __version__,
                "telethon": telethon.__version__
            },
            "teagram.platform": {
                "platform": utils.get_platform()
            },
            "teagram.git": {
                "url": get_git_info(url=True),
                "commit": str(get_git_info(commit=True)),
                "branch": str(get_git_info(branch=True))
            }
        }  

    async def dump_cmd(self, message):
        result = self.gen()

        with open(PATH, 'w') as f:
            json.dump(result, f, indent=4)

        await utils.answer(
            message,
            PATH,
            document=True,
            caption=self.strings("dumped")
        )
    
    @loader.loop(5, autostart=True)
    async def dumploop(self):
        global data
        result = self.gen()
        data = result 
    
    @atexit.register
    def create_dump():
        global data

        with open(PATH, 'w') as f:
            json.dump(data, f, indent=4)

        logger.info(f"Dump file created, {PATH}")

