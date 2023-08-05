import time
import io
import os
import logging
from logging import StreamHandler

from pyrogram import Client, types

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

@loader.module(name="Tester", author="teagram")
class TesterMod(loader.Module):
    """Тест чего-то"""

    async def logs_cmd(self, app: Client, message: types.Message, args: str):
        app.me = await app.get_me()
        """Отправляет логи. Использование: logs <уровень>"""
        if not args:
            args = "40"


        lvl = int(args)

        if not args or lvl < 0 or lvl > 60:
            return await utils.answer(
                message, "❌ Вы не указали уровень или указали неверный уровень логов")

        handler: CustomStreamHandler = log.handlers[1] # type: ignore
        logs = '\n'.join(str(error) for error in handler.logs).encode('utf-8')
        
        if not logs:
            return await utils.answer(
                message, f"❕ Нет логов на уровне {lvl} ({logging.getLevelName(lvl)})")

        logs = io.BytesIO(logs)
        logs.name = "teagram.log"

        return await message.reply_document(
            document=logs,
            caption=f"📤 Teagram Логи с {lvl} ({logging.getLevelName(lvl)}) уровнем"
            )
    
    async def setprefix_cmd(self, app: Client, message: types.Message, args: str):
        """Изменить префикс, можно несколько штук разделённые пробелом. Использование: setprefix <префикс> [префикс, ...]"""
        if not (args := args.split()):
            return await utils.answer(
                message, "❔ На какой префикс нужно изменить?")

        self.db.set("teagram.loader", "prefixes", list(set(args)))
        prefixes = ", ".join(f"<code>{prefix}</code>" for prefix in args)
        return await utils.answer(
            message, f"✅ Префикс был изменен на {prefixes}")

    async def setlang_cmd(self, app: Client, message: types.Message, args: str):
        """Изменить язык. Использование: setlang <язык>"""
        args = args.split()
        
        language = args[0]
        languages = list(map(lambda x: x.replace('.yml', ''), os.listdir('teagram/langpacks')))
        
        if not args:
            return await utils.answer(
                message, "❔ На какой язык нужно изменить?")
        
        if language not in languages:
            langs = ' '.join(languages)
            return await utils.answer(
                message, f'❌ Язык не найден. Доступные языки: <code>{langs}</code>')

        self.db.set("teagram.loader", "lang", language)
        return await utils.answer(
            message, f"✅ Язык был изменен на {language}")

    async def addalias_cmd(self, app: Client, message: types.Message, args: str):
        """Добавить алиас. Использование: addalias <новый алиас> <команда>"""
        if not (args := args.lower().split(maxsplit=1)):
            return await utils.answer(
                message, "❔ Какой алиас нужно добавить?")

        if len(args) != 2:
            return await utils.answer(
                message, "❌ Неверно указаны аргументы."
                        "✅ Правильно: addalias <новый алиас> <команда>"
            )

        aliases = self.all_modules.aliases
        if args[0] in aliases:
            return await utils.answer(
                message, "❌ Такой алиас уже существует")

        if not self.all_modules.command_handlers.get(args[1]):
            return await utils.answer(
                message, "❌ Такой команды нет")

        aliases[args[0]] = args[1]
        self.db.set("teagram.loader", "aliases", aliases)

        return await utils.answer(
            message, f"✅ Алиас <code>{args[0]}</code> для команды <code>{args[1]}</code> был добавлен")

    async def delalias_cmd(self, app: Client, message: types.Message, args: str):
        """Удалить алиас. Использование: delalias <алиас>"""
        if not (args := args.lower()):
            return await utils.answer(
                message, "❔ Какой алиас нужно удалить?")

        aliases = self.all_modules.aliases
        if args not in aliases:
            return await utils.answer(
                message, "❌ Такого алиаса нет")

        del aliases[args]
        self.db.set("teagram.loader", "aliases", aliases)

        return await utils.answer(
            message, f"✅ Алиас <code>{args}</code> был удален")

    async def aliases_cmd(self, app: Client, message: types.Message):
        """Показать все алиасы"""
        aliases = self.all_modules.aliases
        if not aliases:
            return await utils.answer(
                message, "Алиасов нет")

        return await utils.answer(
            message, "🗄 Список всех алиасов:\n" + "\n".join(
                f"• <code>{alias}</code> ➜ {command}"
                for alias, command in aliases.items()
            )
        )

    async def ping_cmd(self, app: Client, message: types.Message, args: str):
        """🍵 команда для просмотра пинга."""
        start = time.perf_counter_ns()
        await utils.answer(message, "☕")
        ping = round((time.perf_counter_ns() - start) / 10**6, 3)
        await utils.answer(
            message,
            f"""
🕒 **Время отлика Telegram**: `{ping}ms`
            """
        )

