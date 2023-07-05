import time
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="ping")
class ping(loader.Module):
    """Узнайте пинг вашего юзер бота"""


    async def ping(self, app: Client, message: types.Message, args: str):
        """Узнайте ваш пинг"""
        start_ping = time.perf_counter_ns()
        await utils.answer(message,"⏳")
        
        await utils.answer(
            message,
            "Твой пинг: " + round((time.perf_counter_ns() - start) / 10**6, 3)
         
         )

