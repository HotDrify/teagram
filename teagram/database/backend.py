import asyncio
from typing import Union

from pyrogram import Client, types


class CloudDatabase:
    """Чат в Telegram с данными для базы данных"""

    def __init__(self, app: Client, me: types.User):
        self._app = app
        self._me = me
        self.data_chat = None
    
    # in future
    #     asyncio.get_event_loop().create_task(
    #         self.find_data_chat())

    # async def find_data_chat(self):
    #     """Информация о чате с данными"""
    #     if not self.data_chat:
    #         chat = [
    #             dialog.chat async for dialog in self._app.get_dialogs()
    #             if dialog.chat.title == f"teagram-{self._me.id}-data"
    #             and dialog.chat.type == "supergroup"
    #         ]

    #         if not chat:
    #             self.data_chat = await self._app.create_supergroup(f"teagram-{self._me.id}-data")
    #         else:
    #             self.data_chat = chat[0]

    #     return self.data_chat

    async def save_data(self, message: Union[types.Message, str]):
        """Сохранить данные в чат"""
        return (
            await self._app.send_message(
                self.data_chat.id, message
            )
            if isinstance(message, str)
            else await message.copy(self.data_chat.id)
        )

    async def get_data(self, message_id: int):
        """Найти данные по айди сообщения"""
        return await self._app.get_messages(
            self.data_chat.id, message_id
        )
