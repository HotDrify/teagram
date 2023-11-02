import os
import sys
import time
import atexit

from telethon import types
from subprocess import check_output, run
from .. import loader, utils, validators
from ..types import Config, ConfigValue
from loguru import logger

from aiogram import Bot
from aiogram.utils.exceptions import CantParseEntities, BotBlocked, Unauthorized

@loader.module(name="Updater", author='teagram')
class UpdateMod(loader.Module):
    """🍵 Обновление с гита teagram"""
    strings = {'name': 'updater'}

    def __init__(self):
        value = self.db.get('Updater', 'sendOnUpdate')

        if value is None:
            value = True

        self.config = Config(
            ConfigValue(
                option='sendOnUpdate',
                docstring='Оповещать об обновлении',
                default=True,
                value=value,
                validator=validators.Boolean()
            )
        )

    async def on_load(self):
        if not self.config.get('sendOnUpdate'):
            return

        bot: Bot = self.bot.bot
        me = await self.client.get_me()

        try:
            _me = await bot.get_me()
        except Unauthorized:
            self.db.set('teagram.bot', 'token', None)
            def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "teagram")

            atexit.register(restart)
            logger.error("Bot is unauthorized, restarting.")
            return sys.exit(0)

        last = None

        try:
            last = utils.git_hash()
            diff = (await utils.run_sync(check_output, 'git rev-parse HEAD', shell=True)).decode().strip()

            if last != diff:
                await bot.send_message(
                    me.id,
                    f"{self.strings['hupdate']} (<a href='https://github.com/itzlayz/teagram-tl/commit/{last}'>{last[:6]}...</a>)"
                )
        except BotBlocked:
            logger.error(f'Updater | {self.strings["nodialog"]} ({_me.username})')

        except CantParseEntities:
            await bot.send_message(
                me.id,
                f"{self.strings['hupdate']} (https://github.com/HotDrify/teagram/commit/{last})"
            )
        except Exception as error:
            await bot.send_message(
                me.id,
                f'{self.strings["eone"]}\n'
                f'{self.strings["etwo"]} {error}'
            )

    async def update_cmd(self, message: types.Message):
        try:
            await utils.answer(message, self.strings['updating'])
            try:
                output = check_output('git pull', shell=True).decode()
            except:
                check_output('git stash', shell=True)
                output = check_output('git pull', shell=True).decode()


            if 'Already up to date.' in output:
                return await utils.answer(message, self.strings['lastver'])

            if 'requirements.txt' in output:
                await utils.answer(message, self.strings['downloading'])
                try:
                    run(
                        [
                            "pip3",
                            "install",
                            "--upgrade",
                            "--disable-pip-version-check",
                            "--no-warn-script-location",
                            "requirements.txt",
                        ],
                        check=True,
                    )
                except:
                    pass

            def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "teagram")

            atexit.register(restart)
            self.db.set(
                "teagram.loader", "restart", {
                    "msg": f"{utils.get_chat(message)}:{message.id}",
                    "start": time.time(),
                    "type": "update"
                }
            )

            await utils.answer(message, self.strings['update'])
            sys.exit(0)
        except Exception as error:
            await utils.answer(message, self.strings['error'].format(error))
