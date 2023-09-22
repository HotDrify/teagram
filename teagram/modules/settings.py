import time
import io
import os
import logging
from logging import StreamHandler

from telethon import types

from .. import loader, utils


class CustomStreamHandler(StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs: list = []

    def emit(self, record):
        self.logs.append(record)

        super().emit(record)

handler = CustomStreamHandler()
log = logging.getLogger()
log.addHandler(handler)

@loader.module(name="Settings", author="teagram")
class SettingsMod(loader.Module):
    """Настройки юзер бота
       Userbot's settings"""

    strings = {'name': 'settings'}

    async def logs_cmd(self, message: types.Message, args: str):
        """Отправляет логи. Использование: logs <уровень>"""
        if not args:
            args = "40"

        lvl = int(args)

        if not args or lvl < 0 or lvl > 60:
            return await utils.answer(
                message, self.strings['no_logs'])

        handler: CustomStreamHandler = log.handlers[1]
        logs = '\n'.join(str(error) for error in handler.logs).encode('utf-8')
        
        if not logs:
            return await utils.answer(
                message, self.strings['no_lvl'].format(lvl=lvl,
                                                 name=logging.getLevelName(lvl)))

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
        
        language = args[0]
        languages = list(map(lambda x: x.replace('.yml', ''), os.listdir('teagram/langpacks')))
        
        if not args:
            return await utils.answer(
                message, self.strings['wlang'])
        
        if language not in languages:
            langs = ' '.join(languages)
            return await utils.answer(
                message, self.strings['elang'].format(langs=langs))

        self.db.set("teagram.loader", "lang", language)
        
        pack = utils.get_langpack()
        for instance in self.manager.modules:
            if (name := getattr(instance, 'strings', '')):
                print(name.get('name', ''))
                if (stringsname := name.get('name', '').lower()) in [
                    'backup',
                    'config',
                    'eval',
                    'help',
                    'info',
                    'loader',
                    'moduleguard',
                    'settings',
                    'terminal',
                    'translator',
                    'updater'
                ]:
                    pack = pack.get(stringsname)
                    pack['name'] = stringsname
                    instance.strings = pack.get(stringsname)

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

    async def ping_cmd(self, message: types.Message, args: str):
        """🍵 команда для просмотра пинга."""
        start = time.perf_counter_ns()
        
        msg = await message._client.send_message(utils.get_chat(message), "☕")
        
        ping = round((time.perf_counter_ns() - start) / 10**6, 3)

        await utils.answer(
            message,
            f"🕒 <b>{self.strings['ping']}</b>: <code>{ping}ms</code>"
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