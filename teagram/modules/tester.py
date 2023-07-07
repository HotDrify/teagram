import io
import logging
from datetime import datetime

from pyrogram import Client, types

from .. import loader, logger, utils


@loader.module(name="Tester", author="teagram")
class TesterMod(loader.Module):
    """Тест чего-то"""
    async def logscmd(self, app: Client, message: types.Message, args: str):
        """Отправляет логи. Использование: logs <уровень>"""
        lvl = 40  # ERROR

        if args and not (lvl := logger.get_valid_level(args)):
            return await utils.answer(
                message, "❌ Неверный уровень логов")

        handler = logging.getLogger().handlers[0]
        logs = ("\n".join(handler.dumps(lvl))).encode("utf-8")
        if not logs:
            return await utils.answer(
                message, f"❕ Нет логов на уровне {lvl} ({logging.getLevelName(lvl)})")

        logs = io.BytesIO(logs)
        logs.name = "teagram.log"

        await message.delete()
        return await utils.answer(
            message, logs, doc=True, quote=False,
            caption=f"📤 TeagramЛоги с {lvl} ({logging.getLevelName(lvl)}) уровнем"
        )