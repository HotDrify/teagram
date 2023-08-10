import os
import sys
import time
import atexit
import logging
import traceback

from pyrogram import Client, types
from subprocess import check_output
from .. import loader, utils
from aiogram import Bot

from aiogram.utils.exceptions import CantParseEntities


@loader.module(name="Updater", author='teagram')
class UpdateMod(loader.Module):
    """🍵 Обновление с гита teagram"""
    async def on_load(self, app: Client):
        bot: Bot = self.bot.bot
        me = await app.get_me()
        
        last = None
        local = None

        try:
            last = check_output('git log -1', shell=True).split()[1]
            local = check_output('git rev-parse HEAD', shell=True)

            if last != local:
                await bot.send_message(
                me.id,
                f"✔ Доступно обновление (<a href='https://github.com/HotDrify/teagram/commit/{last}'>{last[:6]}</a>)"
                )

        except CantParseEntities:
            if last != local:
                await bot.send_message(
                    me.id,
                    f"✔ Доступно обновление (https://github.com/HotDrify/teagram/commit/{last})"
                )
                
        except Exception as error:
            traceback.print_exc()
            await bot.send_message(
                me.id,
                '❌ Произошла ошибка, при проверке доступного обновления.\n'
                f'❌ Пожалуйста, удостовертесь что у вас работает команда GIT {error}'
            )

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
