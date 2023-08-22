import os
import zipfile

from telethon import TelegramClient, types

from .. import loader, utils, wrappers
from loguru import logger
from time import time

@wrappers.wrap_function_to_async
def create_backup(src: str, dest: str):
    name = f'backup_{round(time())}'
    exceptions = [name, 'backup', 'session', 'db', 'config', 'bot_avatar']
    
    zipp = os.path.join(dest, f'{name}.zip')

    try:
        with zipfile.ZipFile(zipp, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(src):
                for file in files:
                    exceptionn = False

                    for exception in exceptions:
                        if exception in file:
                            exceptionn = True
                        elif exceptionn:
                            break
                    
                    if not exceptionn:
                        path = os.path.join(root, file)
                        arcname = os.path.relpath(path, src)
                        zipf.write(path, arcname)

        return [zipp, True]
    except Exception as error:
        return [str(error), False, zipp] 

@loader.module(name="Backuper", author='teagram')
class BackupMod(loader.Module):
    """С помощью этого модуля вы сможете делать бекапы модов и всего ЮБ"""
    async def backupub_cmd(self, app: TelegramClient, message: types.Message):
        """Бекап ЮБ"""
        message = await app.send_message(
            message.chat.id,
            '👀 Попытка бекапа...'
        )

        backup = await create_backup('./', '')

        if backup[1]:
            return await app.send_message(
                message.chat.id,
                f'✅ Успешно сохранено ({backup[0]})'
            )
        else:
            logger.error(backup[0])

            return await app.send_message(
                message.chat.id,
                f'❌ Ошибка, проверьте логи (возможный бекап {backup[2]})'
            )
        
    async def backupmods_cmd(self, app: TelegramClient, message: types.Message):
        """Бекап модулей"""
        await app.send_message(
            message.chat.id,
            '👀 Попытка бекапа...'
        )

        backup = await create_backup('./teagram/modules/', '')

        if backup[1]:
            return await app.send_message(
                message.chat.id,
                f'✅ Успешно сохранено ({backup[0]})'
            )
        else:
            logger.error(backup[0])

            return await app.send_message(
                message.chat.id,
                f'❌ Ошибка, проверьте логи (возможный бекап {backup[2]})'
            )
        
