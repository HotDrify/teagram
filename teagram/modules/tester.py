import io
import logging
from datetime import datetime
from logging import StreamHandler

from pyrogram import Client, types

from .. import loader, logger, utils

class CustomStreamHandler(logging.StreamHandler):
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
        lvl = 40  # ERROR

        if args and not (lvl := logger.get_valid_level(args)):
            return await utils.answer(
                message, "❌ Неверный уровень логов")

        handler: CustomStreamHandler = log.handlers[1]
        logs = '\n'.join(str(error) for error in handler.logs).encode('utf-8')
        if not logs:
            return await utils.answer(
                message, f"❕ Нет логов на уровне {lvl} ({logging.getLevelName(lvl)})")

        logs = io.BytesIO(logs)
        logs.name = "teagram.log"

        return await utils.answer(
            message, logs, doc=True, quote=False,
            caption=f"📤 TeaGram Логи с {lvl} ({logging.getLevelName(lvl)}) уровнем"
            )
