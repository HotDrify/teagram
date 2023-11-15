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

import time
import io
import os
import logging

from logging import _nameToLevel, _levelToName
from datetime import timedelta
from telethon import types, TelegramClient
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import loader, utils, bot

log = logging.getLogger()

class TestException(Exception):
    pass

@loader.module(name="Settings", author="teagram")
class SettingsMod(loader.Module):
    """Настройки юзер бота
       Userbot's settings"""

    strings = {'name': 'settings'}
    levels = "\n".join(f"<code>{k}</code>: <code>{v}</code>" for k, v in _nameToLevel.items())

    async def logs_cmd(self, message: types.Message, args: str):
        """Отправляет логи. Использование: logs <уровень>"""
        try:
            args = int(args)
        except:
            args = args.strip().upper()

        if not args or (
            (args < 0 or args > 50) if isinstance(args, int)
            else (_nameToLevel.get(args, '') and _levelToName.get(args, ''))
        ):
            return await utils.answer(
                message, self.strings['no_logs'] + self.levels)

        if not getattr(self, '_logger', ''):
            self._logger = log.handlers[0]

        lvl = logging.getLevelName(args)
        if isinstance(lvl, int):
            lvl = _levelToName.get(lvl)
        
        if not self._logger.logs[lvl]:
            return await utils.answer(
                message, self.strings["no_logs_at_lvl"] # Будет переведено, лейз не абижайся(
            )
        
        logs = '\n'.join(
            self._logger.format(log) for log in self._logger.logs[lvl]
        ).encode('utf-8')
        
        if not logs:
            return await utils.answer(
                message, self.strings['no_lvl'].format(
                    lvl=lvl,
                    name=logging.getLevelName(lvl)
                ) + self.levels
            )
        
        logs = io.BytesIO(logs)
        logs.name = "teagram.log"

        return await utils.answer(
            message,
            logs,
            document=True,
            caption=self.strings['logs'].format(
                lvl=lvl, 
                name=logging.getLevelName(lvl))
            )

    @loader.command()
    async def clearlogs(self, message: types.Message):
        if not getattr(self, '_logger', ''):
            self._logger = log.handlers[0]

        self._logger.flush()
        self._logger.logs = {
            'INFO': [],
            'WARNING': [],
            'ERROR': [],
            'CRITICAL': [],
            'DEBUG': [],
            'NOTSET': []
        }

        await utils.answer(message, self.strings['flushed'])

    @loader.command()
    async def error(self, message):
        raise TestException("Test exception")

    async def setprefix_cmd(self, message: types.Message, args: str):
        """Изменить префикс, можно несколько штук разделённые пробелом. Использование: setprefix <префикс> [префикс, ...]"""
        if not (args := args.split()):
            return await utils.answer(
                message, self.strings['wprefix'])

        self.db.set("teagram.loader", "prefixes", list(set(args)))
        prefixes = ", ".join(f"<code>{prefix}</code>" for prefix in args)
        await utils.answer(
            message, self.strings['prefix'].format(prefixes=prefixes))

    async def setlang_cmd(self, message: types.Message, args: str):
        """Изменить язык. Использование: setlang <язык>"""
        args = args.split()

        languages = list(map(lambda x: x.replace('.yml', ''), os.listdir('teagram/langpacks')))
        langs = f" (<code>{', '.join(languages)}</code>)"

        if not args:
            return await utils.answer(
                message, self.strings['wlang'] + langs)

        language = args[0]

        if language not in languages:
            langs = ' '.join(languages)
            return await utils.answer(
                message, self.strings['elang'].format(langs=langs))

        self.db.set("teagram.loader", "lang", language)
        self.manager.translator.load_translation()

        return await utils.answer(
            message, self.strings['lang'].format(language=language))

    async def addalias_cmd(self, message: types.Message, args: str):
        """Добавить алиас. Использование: addalias <новый алиас> <команда>"""
        if not (args := args.lower().split(maxsplit=1)):
            return await utils.answer(
                message, self.strings['walias'])

        if len(args) != 2:
            return await utils.answer(
                message, self.strings['ealias']
            )

        aliases = self.manager.aliases
        if args[0] in aliases:
            return await utils.answer(
                message, self.strings['nalias'])

        if not self.manager.command_handlers.get(args[1]):
            return await utils.answer(
                message, self.strings['calias'])

        aliases[args[0]] = args[1]
        self.db.set("teagram.loader", "aliases", aliases)

        return await utils.answer(
            message, self.strings['alias'].format(alias=args[0], cmd=args[1]))

    async def delalias_cmd(self, message: types.Message, args: str):
        """Удалить алиас. Использование: delalias <алиас>"""
        if not (args := args.lower()):
            return await utils.answer(
                message, self.strings['dwalias'])

        aliases = self.manager.aliases
        if args not in aliases:
            return await utils.answer(
                message, self.strings['dealias'])

        del aliases[args]
        self.db.set("teagram.loader", "aliases", aliases)

        return await utils.answer(
            message, self.strings['dalias'].format(args))

    async def aliases_cmd(self, message: types.Message):
        """Показать все алиасы"""
        if aliases := self.manager.aliases:
            return await utils.answer(
                message, self.strings['allalias'] + "\n".join(
                    f"• <code>{alias}</code> ➜ {command}"
                    for alias, command in aliases.items()
                )
            )
        else:
            return await utils.answer(
                message, self.strings['noalias'])

    async def ping_cmd(self, message: types.Message):
        """🍵 команда для просмотра пинга."""
        start = time.perf_counter_ns()
        client: TelegramClient = message._client
        msg = await client.send_message(utils.get_chat(message), "☕", reply_to=utils.get_topic(message))

        ping = round((time.perf_counter_ns() - start) / 10**6, 3)
        uptime = timedelta(seconds=round(time.time() - utils._init_time))

        await utils.answer(
            message,
            f"🕒 {self.strings['ping']}: <code>{ping}ms</code>\n"
            f"❔ {self.strings['uptime']}: <code>{uptime}</code>"
        )

        await msg.delete()

    @loader.command()
    async def adduser(self, message: types.Message):
        if not (reply := await message.message.get_reply_message()):
            return await utils.answer(
                message,
                self.strings['noreply']
            )

        if reply.sender_id == (_id := (await self.client.get_me()).id):
            return await utils.answer(
                message,
                self.strings['yourself']
            )

        if message.message.sender_id != _id:
            return await utils.answer(
                message,
                self.strings['owner']
            )

        user = reply.sender_id
        users = self.db.get('teagram.loader', 'users', [])
        self.db.set('teagram.loader', 'users', users + [user])

        await utils.answer(message, self.strings['adduser'])

    @loader.command()
    async def rmuser(self, message: types.Message):
        if not (reply := await message.message.get_reply_message()):
            return await utils.answer(
                message,
                self.strings['noreply']
            )

        if reply.sender_id == (_id := (await self.client.get_me()).id):
            return await utils.answer(
                message,
                self.strings['yourself']
            )

        if message.message.sender_id != _id:
            return await utils.answer(
                message,
                self.strings['owner']
            )

        user = reply.sender_id
        users = self.db.get('teagram.loader', 'users', [])
        self.db.set('teagram.loader', 'users', list(filter(lambda x: x != user, users)))

        await utils.answer(message, self.strings['deluser'])

    @loader.command()
    async def users(self, message: types.Message):
        _users = self.db.get('teagram.loader', 'users', [])
        await utils.answer(
            message,
            (f'➡ {self.strings["user"]} <code>' + ', '.join(str(user) for user in _users) + '</code>')
              if _users else self.strings['nouser']
        )

    @loader.command()
    async def ch_token(self, message: types.Message):
        self.db.set('teagram.bot', 'token', None)
        await utils.answer(
            message, self.strings['chbot'].format(f"{self.prefix}restart")
        )