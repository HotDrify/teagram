import logging

import os
import re
import sys
import time


import atexit

import requests

from typing import List

from telethon import types
from telethon.tl.custom import Message
from .. import loader, utils

VALID_URL = r"[-[\]_.~:/?#@!$&'()*+,;%<=>a-zA-Z0-9]+"
VALID_PIP_PACKAGES = re.compile(
    r"^\s*# required:(?: ?)((?:{url} )*(?:{url}))\s*$".format(url=VALID_URL),
    re.MULTILINE,
)


@loader.module(name="Loader", author='teagram')
class LoaderMod(loader.Module):
    """Загрузчик модулей"""

    async def loadraw_cmd(self, message: Message, args: str):
        if not args:
            return await utils.answer(
                message,
                '❌ Вы не указали ссылку'
            )
        
        try:
            response = await utils.run_sync(requests.get, args)
            module = await self.manager.load_module(response.text, response.url)

            if module is True:
                return await utils.answer(
                    message, "✅ Зависимости установлены. Требуется перезагрузка")

            if not module:
                return await utils.answer(
                    message, "❌ Не удалось загрузить модуль. Подробности смотри в логах")

            
            await utils.answer(
                message, 
                f"✅ Модуль \"<code>{module}</code>\" загружен"
            )

        except requests.exceptions.MissingSchema:
            await utils.answer(message, '❌ Вы указали неправильную ссылку')
        except Exception as error:
            await utils.answer(message, f'❌ Ошибка: <code>{error}</code>')

    async def loadmod_cmd(self,  message: Message):
        """Загрузить модуль по файлу. Использование: <реплай на файл>"""
        reply: Message = await message.get_reply_message()
        file = (
            message
            if message.document
            else reply
            if reply and reply.document
            else None
        )

        if not file:
            return await utils.answer(
                message, "❌ Нет реплая на файл")

        _file = await reply.download_media(bytes)

        try:
            _file = _file.decode()
        except UnicodeDecodeError:
            return await utils.answer(
                message, "❌ Неверная кодировка файла")

        modules = [
            '_example'
            'config',
            'eval',
            'help',
            'info',
            'moduleGuard',
            'terminal',
            'tester',
            'updater'
        ]
        
        for mod in modules:
            if _file == mod:
                return await utils.answer(
                    message,
                    "❌ Нельзя загружать встроенные модули"
                )

        module_name = await self.manager.load_module(_file)
        module = '_'.join(module_name.lower().split())

        if module_name is True:
            with open(f'teagram/modules/{module}.py', 'w', encoding="utf-8") as file:
                file.write(_file)

            return await utils.answer(
                message, "✅ <b>Зависимости установлены. Требуется перезагрузка</b>")

        if not module_name:
            return await utils.answer(
                message, "❌ <b>Не удалось загрузить модуль. Подробности смотри в логах</b>")
        
        with open(f'teagram/modules/{module}.py', 'w', encoding="utf-8") as file:
            file.write(_file)
        
        await utils.answer(
            message, f"✅ Модуль \"<code>{module_name}</code>\" загружен")

    async def unloadmod_cmd(self,  message: types.Message, args: str):
        """Выгрузить модуль. Использование: unloadmod <название модуля>"""
        if not (module_name := self.manager.unload_module(args)):
            return await utils.answer(
                message, "❌ Неверное название модуля")
        
        modules = [
            'config',
            'eval',
            'help',
            'info',
            'moduleGuard',
            'terminal',
            'tester',
            'updater',
            'loader'
        ]
        
        if module_name in modules:
            return await utils.answer(
                message,
                "❌ Выгружать встроенные модули нельзя"
            )

        return await utils.answer(
            message, f"✅ Модуль \"<code>{module_name}</code>\" выгружен")
    
    async def reloadmod_cmd(self,  message: types.Message, args: str):
        if not args:
            return await utils.answer(
                message, "❌ Вы не указали модуль")
        
        try:
            module = args.split(maxsplit=1)[0].replace('.py', '')

            modules = [
                'config',
                'eval',
                'help',
                'info',
                'moduleGuard',
                'terminal',
                'tester',
                'updater',
                'loader'
            ]
            
            # for mod in modules:
            #     if module == mod:
            #         return await utils.answer(
            #             message,
            #             "❌ Нельзя перезагружать встроенные модули"
            #         )

            if module + '.py' not in os.listdir('teagram/modules'):
                return await utils.answer(
                    message,
                    f'❌ Модуль {module} не найден'
                )
            
            unload = self.manager.unload_module(module)
            with open(f'teagram/modules/{module}.py', encoding='utf-8') as file:
                module_source = file.read()

            load = await self.manager.load_module(module_source)

            if not load and not unload:
                return await utils.answer(
                    message,
                    '❌ Произошла ошибка, пожалуйста проверьте логи'
                )
        except Exception as error:
            logging.error(error)
            return await utils.answer(
                message,
                '❌ Произошла ошибка, пожалуйста проверьте логи'
            )


        return await utils.answer(
            message, f"✅ Модуль \"<code>{module}</code>\" перезагружен")

    async def restart_cmd(self, message: types.Message):
        """Перезагрузка юзербота"""
        def restart() -> None:
            """Запускает загрузку юзербота"""
            os.execl(sys.executable, sys.executable, "-m", "teagram")

        atexit.register(restart)
        self.db.set(
            "teagram.loader", "restart", {
                "msg": f"{((message.chat.id) if message.chat else 0 or message._chat_peer)}:{message.id}",
                "start": time.time(),
                "type": "restart"
            }
        )

        await utils.answer(message, "<b><emoji id=5328274090262275771>🔁</emoji> Перезагрузка...</b>")

        logging.info("Перезагрузка...")
        return sys.exit(0)
    