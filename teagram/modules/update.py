import os
import sys
import atexit
import logging

from pyrogram import Client, types
from subprocess import check_output
from .. import loader, utils


@loader.module(name="updater")
class UpdateMod(loader.Module):
    """🍵 Обновление с гита teagram"""

    async def update_cmd(self, app: Client, message: types.Message):
        try:
            output = check_output('git pull', shell=True).decode()
            
            if 'Already up to date.' in output:
                return await utils.answer(message, '`🍵 | TeaGram`\n<b>У вас установлена последняя версия</b>')
            
            def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "teagram")

            atexit.register(restart)
            self.db.set(
                "teagram.loader", "restart", {
                    "msg": f"{message.chat.id}:{message.id}",
                    "type": "restart"
                }
            )

            await utils.answer(message, "🔁 Перезагрузка...")

            logging.info("Перезагрузка...")
            return sys.exit(0)
        except Exception as error:
            await utils.answer(message, f'Произошла ошибка: {error}')
