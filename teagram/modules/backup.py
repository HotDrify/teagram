from telethon import types, TelegramClient
from .. import loader, utils, validators
from ..types import Config, ConfigValue

from loguru import logger

import os
import zipfile
import asyncio
from time import time
from ..wrappers import wrap_function_to_async

@wrap_function_to_async
def create_backup(src: str, dest: str, db=False):
    name = f'backup_{round(time())}'
    exceptions = [name, 'backup', 'session', 'db', 'config', 'bot_avatar']
    zipp = os.path.join(dest, f'{name}.zip')

    try:
        with zipfile.ZipFile(zipp, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(src):
                for file in files:
                    exceptionn = False
                    if not db:
                        for exception in exceptions:
                            if 'db.json' in file:
                                break

                            if exception in file:
                                exceptionn = True
                            elif exceptionn:
                                break

                if not exceptionn:
                    if '.git' in root or 'venv' in root:
                        continue

                    path = os.path.join(root, file)
                    arcname = os.path.relpath(path, src)
                    zipf.write(path, arcname)

        return [zipp, True]
    except Exception as error:
        return [str(error), False, zipp]

@loader.module(name="Backuper", author='teagram')
class BackupMod(loader.Module):
    """С помощью этого модуля вы сможете делать бекапы модов и всего ЮБ"""
    strings = {
        'success': '<b>✔ Успешно сохранено ({})</b>'.format,
        'error': '<b>❌ Ошибка, проверьте логи</b>',
        'reply': '<b>❌ Ошибка, вы не указали реплай с файлом</b>'
    }

    def __init__(self):
        self.config = Config(
            ConfigValue(
                option='backupInterval',
                docstring='⌛ Время через которое будет сделан бекап (В секундах)',
                default=86400,
                value=self.db.get('Backuper', 'backupInterval', 86400),
                validator=validators.Integer(minimum=43200)
            )
        )

    async def on_load(self):
        if self.config['backupInterval']:
            self.toloop.start()

    @loader.loop(1, autostart=True)
    async def toloop(self):
        if not (interval := self.config['backupInterval']):
            await asyncio.sleep(10)

        self.client: TelegramClient
        backup = await create_backup('./teagram/modules/', '')

        if backup[1]:
            await self.client.send_file(
                await self.db.cloud.get_chat(),
                backup[0],
                caption=self.strings['success'](''),
                parse_mode='html'
            )
        else:
            logger.error(backup[0])
            await self.client.send_message(
                await self.db.cloud.get_chat(),
                self.strings['error'],
                parse_mode='html'
            )
        
        await asyncio.sleep(interval)

    @loader.command('Backup mods')
    async def backupmods(self, message: types.Message):
        """Бекап модулей"""
        await utils.answer(
            message,
            '👀 Попытка бекапа...'
        )

        backup = await create_backup('./teagram/modules/', '')

        if backup[1]:
            await utils.answer(
                message,
                backup[0],
                document=True,
                caption=self.strings['success']('')
            )
        else:
            logger.error(backup[0])

            await utils.answer(
                message,
                self.strings['error']
            )

    @loader.command('Backup db')
    async def backupdb(self, message: types.Message):
        await utils.answer(
            message,
            '👀 Попытка бекапа...'
        )

        backup = await create_backup('.', '', True)

        if backup[1]:
            await utils.answer(
                message,
                self.strings['success'](backup[0])
            )
        else:
            logger.error(backup[0])

            await utils.answer(
                message,
                self.strings['error']
            )
