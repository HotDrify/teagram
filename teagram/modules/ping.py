import time
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="ping")
class ping(loader.Module):
    """🍵 пинг юзербота."""


    async def pingcmd(self, app: Client, message: types.Message, args: str):
        """🍵 команда для просмотра пинга."""
        start_ping = time.perf_counter_ns()
        await utils.answer(message,"☕")
        ping = round((time.perf_counter_ns() - start) / 10**6, 3)
        await utils.answer(
            message,
            f"""
🍵 `Teagram | UserBot`
🏓 **Понг!**: `{ping}ms`
            """
         )

