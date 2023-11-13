#                            ██╗████████╗███████╗██╗░░░░░░█████╗░██╗░░░██╗███████╗
#                            ██║╚══██╔══╝╚════██║██║░░░░░██╔══██╗╚██╗░██╔╝╚════██║
#                            ██║░░░██║░░░░░███╔═╝██║░░░░░███████║░╚████╔╝░░░███╔═╝
#                            ██║░░░██║░░░██╔══╝░░██║░░░░░██╔══██║░░╚██╔╝░░██╔══╝░░
#                            ██║░░░██║░░░███████╗███████╗██║░░██║░░░██║░░░███████╗
#                            ╚═╝░░░╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
#                                            https://t.me/itzlayz
#                           
#                                    🔒 Licensed under the GNU AGPLv3
#                                 https://www.gnu.org/licenses/agpl-3.0.html

import logging

import os
import re
import sys
import time


import atexit
import requests

from telethon import types
from telethon.tl.custom import Message
from .. import loader, utils

VALID_URL = r"[-[\]_.~:/?#@!$&'()*+,;%<=>a-zA-Z0-9]+"
VALID_PIP_PACKAGES = re.compile(
    r"^\s*# required:(?: ?)((?:{url} )*(?:{url}))\s*$".format(url=VALID_URL),
    re.MULTILINE,
)

GIT_REGEX = re.compile(
    r"^https?://github\.com((?:/[a-z0-9-]+){2})(?:/tree/([a-z0-9-]+)((?:/[a-z0-9-]+)*))?/?$",
    flags=re.IGNORECASE,
)

async def get_git_raw_link(repo_url: str):
    """Получить raw ссылку на репозиторий"""
    match = GIT_REGEX.search(repo_url)
    if not match:
        return False

    repo_path = match.group(1)
    branch = match.group(2)
    path = match.group(3)

    r = await utils.run_sync(requests.get, f"https://api.github.com/repos{repo_path}")
    if r.status_code != 200:
        return False

    branch = branch or r.json()["default_branch"]

    return f"https://raw.githubusercontent.com{repo_path}/{branch}{path or ''}/"

@loader.module(name="Loader", author='teagram')
class LoaderMod(loader.Module):
    """Загрузчик модулей"""
    strings = {'name': 'loader'}
    async def repo_cmd(self, message: types.Message, args: str):
        """Установить репозиторий с модулями. Использование: repo <ссылка на репозиторий или reset>"""
        if not args:
            return await utils.answer(
                message, self.strings['noargs'])

        if args == "reset":
            self.db.set(
                "teagram.loader", "repo",
                "https://github.com/itzlayz/teagram-modules"
            )
            return await utils.answer(
                message, self.strings['urlrepo'])

        if not await get_git_raw_link(args):
            return await utils.answer(
                message, self.strings['wrongurl'])

        self.db.set("teagram.loader", "repo", args)
        return await utils.answer(
            message, self.strings['yesurl'])

    async def dlrepo_cmd(self, message: types.Message, args: str):
        """Загрузить модуль по ссылке. Использование: dlrepo <ссылка или all или ничего>"""
        modules_repo = self.db.get(
            "teagram.loader", "repo",
            "https://github.com/itzlayz/teagram-modules"
        )
        api_result = await get_git_raw_link(modules_repo)
        if not api_result:
            return await utils.answer(
                message, self.strings['errapi']
            )

        raw_link = api_result
        modules = await utils.run_sync(requests.get, f"{raw_link}all.txt")
        if modules.status_code != 200:
            return await utils.answer(
                message, 
                self.strings['noalltxt'].format(
                    modules_repo=modules_repo
                )
            )

        modules = modules.text.splitlines()

        if not args:
            text = (
                self.strings["listmods"].format(modules_repo=modules_repo)
                + "\n".join(
                    map("<code>{}</code>".format, modules))
            )
            return await utils.answer(
                message, text, link_preview=False)

        error_text = None
        module_name = None
        count = 0

        if args == "all":
            for module in modules:
                module = raw_link + module + ".py"
                try:
                    r = await utils.run_sync(requests.get, module)
                    if r.status_code != 200:
                        raise requests.exceptions.RequestException
                except requests.exceptions.RequestException:
                    continue

                if not (module_name := await self.manager.load_module(r.text, r.url)):
                    continue

                self.db.set("teagram.loader", "modules",
                            list(set(self.db.get("teagram.loader", "modules", []) + [module])))
                count += 1
        else:
            if args in modules:
                args = raw_link + args + ".py"

            try:
                r = await utils.run_sync(requests.get, args)
                if r.status_code != 200:
                    raise requests.exceptions.ConnectionError

                module_name = await self.manager.load_module(r.text, r.url)
                if module_name is True:
                    error_text = self.strings['downdedreq']

                if not module_name:
                    error_text = self.strings['errmod']
            except requests.exceptions.MissingSchema:
                error_text = self.strings['wrongurl']
            except requests.exceptions.ConnectionError:
                error_text = self.strings['modurlerr']
            except requests.exceptions.RequestException:
                error_text = self.strings['reqerr']

            if error_text:
                return await utils.answer(message, error_text)

            self.db.set("teagram.loader", "modules",
                        list(set(self.db.get("teagram.loader", "modules", []) + [args])))

        return await utils.answer(
            message, (
                self.strings['loadedmod'].format(module_name)
                if args != "all"
                else self.strings['loaded'].format(count, len(modules))
            )
        )

    async def dlmod_cmd(self, message: Message, args: str):
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
                    message, self.strings['downdedreq'])

            if not module:
                return await utils.answer(
                    message, self.strings['errmod'])

            with open(f'teagram/modules/{module}.py', 'w', encoding="utf-8") as file:
                file.write(response.text)
            
            await utils.answer(
                message, 
                self.strings['loadedmod'].format(module)
            )

        except requests.exceptions.MissingSchema:
            await utils.answer(message, self.strings['wrongurl'])
        except Exception as error:
            await utils.answer(message, f'❌ <code>{error}</code>')

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
                message, self.strings['noreply'])

        _file = await reply.download_media(bytes)

        try:
            _file = _file.decode()
        except UnicodeDecodeError:
            return await utils.answer(
                message, self.strings['errunicode'])

        modules = [
            '_example'
            'config',
            'eval',
            'help',
            'info',
            'terminal',
            'tester',
            'updater'
        ]
        
        for mod in modules:
            if _file == mod:
                return await utils.answer(
                    message,
                    self.strings['cantload']
                )

        module_name = await self.manager.load_module(_file)
        if not module_name:
            return await utils.answer(
                message, self.strings['noreq'])
        
        module = '_'.join(module_name.lower().split())

        if module_name is True:
            with open(f'teagram/modules/{module}.py', 'w', encoding="utf-8") as file:
                file.write(_file)

            return await utils.answer(
                message, self.strings['downdedreq'])

        if not module_name:
            return await utils.answer(
                message, self.strings['errmod'])
        
        with open(f'teagram/modules/{module}.py', 'w', encoding="utf-8") as file:
            file.write(_file)
        
        await utils.answer(
            message, self.strings['loadedmod'].format(module_name))

    async def unloadmod_cmd(self,  message: types.Message, args: str):
        """Выгрузить модуль. Использование: unloadmod <название модуля>"""
        if not (module_name := self.manager.unload_module(args.strip())):
            return await utils.answer(
                message, self.strings['notfound'].format(args.strip()))
        
        modules = [
            'config',
            'eval',
            'help',
            'info',
            'terminal',
            'tester',
            'updater',
            'loader'
        ]
        
        if module_name in modules:
            return await utils.answer(
                message,
                self.strings['cantunload']
            )

        return await utils.answer(
            message, self.strings['unloadedmod'].format(module_name))
    
    async def reloadmod_cmd(self,  message: types.Message, args: str):
        if not args:
            return await utils.answer(
                message, self.strings['noargs'])

        try:
            module = args.split(maxsplit=1)[0].replace('.py', '')

            modules = [
                'config',
                'eval',
                'help',
                'info',
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

            if f'{module}.py' not in os.listdir('teagram/modules'):
                return await utils.answer(
                    message,
                    self.strings['notfound'].format(module)
                )

            unload = self.manager.unload_module(module)
            with open(f'teagram/modules/{module}.py', encoding='utf-8') as file:
                module_source = file.read()

            load = await self.manager.load_module(module_source)

            if not load and not unload:
                return await utils.answer(
                    message,
                    self.strings['reqerr']
                )
        except Exception as error:
            logging.error(error)
            return await utils.answer(
                message,
                self.strings['basicerr']
            )


        return await utils.answer(
            message, self.strings['reloaded'].format(module))
    
    @loader.command('Скинуть модуль из папки модулей')
    async def showmod(self, message: types.Message, args):
        if not (mod := args.split()) or f'{mod[0]}.py' not in os.listdir(
            'teagram/modules'
        ):
            return await utils.answer(message, self.strings['wrongmod'])

        await utils.answer(
            message, 
            f'teagram/modules/{mod[0]}.py',
            document=True,
            caption=self.strings['replymod'].format(mod[0])+'\n'
            +self.strings['replytoload'].format(self.prefix[0])
        )


    async def restart_cmd(self, message: types.Message):
        """Перезагрузка юзербота"""
        def restart() -> None:
            os.execl(sys.executable, sys.executable, "-m", "teagram")

        atexit.register(restart)
        self.db.set(
            "teagram.loader", "restart", {
                "msg": f"{((message.chat.id) if message.chat else 0 or message._chat_peer)}:{message.id}",
                "start": time.time(),
                "type": "restart"
            }
        )

        await utils.answer(message, self.strings['restarting'])
        sys.exit(0)
    