import asyncio
from typing import Union

from telethon import TelegramClient, types
from ..utils import create_group

class CloudDatabase:
    """
    Cloud database. Essentially, it's a Telegram chat used for sending various logs.
    """

    def __init__(self, app: TelegramClient, me: types.User):
        """
        Initialize the CloudDatabase instance.

        Args:
            app (TelegramClient): The Telegram client instance.
            me (types.User): The user associated with the Telegram client.
        """
        self._app = app
        self._me = me
        self.chat = None

        asyncio.get_event_loop().create_task(self.get_chat())

    async def get_chat(self):
        if not self.chat:
            chat = None
            
            async for dialog in self._app.iter_dialogs():
                if dialog.name == 'teagram-logs':
                    chat = dialog

                    break

            if not chat:
                self.chat = (
                    await create_group(
                        self._app,
                        'teagram-logs', 
                        'Here teagram logs'
                    )
                ).__dict__["chats"][0].__dict__["id"]
            else:
                self.chat = chat

        return self.chat

    async def send_data(self, message: Union[types.Message, str]):
        """Send data to the chat."""
        return (
            await self._app.send_message(
                self.chat, message
            )
            if isinstance(message, str)
            else await self._app.forward_messages(self.chat, message)
        )

    async def get_data(self, message_id: int):
        """Retrieve data using a message ID."""
        return await self._app.get_messages(
            self.chat, message_id
        )
