import os
import shutil
import zipfile

from pyrogram import Client, types

from .. import loader, utils
from loguru import logger
from time import time

def create_backup(src: str, dest: str):
    try:
        name = f'backup_{round(time())}'

        zipp = os.path.join(dest, f'{name}.zip')
        with zipfile.ZipFile(zipp, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(src):
                for file in files:
                    path = os.path.join(root, file)
                    arcname = os.path.relpath(path, src)
                    zipf.write(path, arcname)

        return [zipp, True]
    except Exception as error:
        return [str(error), False] 

@loader.module(name="Backuper", author='teagram')
class BackupMod(loader.Module):
    async def backup_cmd(self, app: Client, message: types.Message):
        backup = create_backup('./', '')

        if backup[1]:
            return await utils.answer(
                message,
                f'✅ Успешно сохранено ({backup[0]})'
            )
        else:
            logger.error(backup[0])

            return await utils.answer(
                message,
                '❌ Ошибка, проверьте логи'
            )
        