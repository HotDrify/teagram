import os
import sys
import time
import atexit
import logging

from pyrogram import Client, types
from subprocess import check_output
from .. import loader, utils


@loader.module(name="Updater", author='teagram')
class UpdateMod(loader.Module):
    """🍵 Обновление с гита teagram"""

    async def update_cmd(self, app: Client, message: types.Message):
        try:
            await utils.answer(message, 'Попытка обновления...')

            check_output('git stash', shell=True).decode()
            output = check_output('git pull', shell=True).decode()
            
            if 'Already up to date.' in output:
                return await utils.answer(message, 'У вас установлена последняя версия ✔')
            
            def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "teagram")

            atexit.register(restart)
            self.db.set(
                "teagram.loader", "restart", {
                    "msg": f"{message.chat.id}:{message.id}",
                    "start": str(round(time.time())),
                    "type": "update"
                }
            )

            await utils.answer(message, "🔁 Обновление...")

            logging.info("Обновление...")
            return sys.exit(0)
        except Exception as error:
            await utils.answer(message, f'Произошла ошибка: {error}')
