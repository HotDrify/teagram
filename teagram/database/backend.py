from typing import Union

from telethon import TelegramClient, types
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto

from ..utils import create_group, BASE_PATH

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
        self._client = app
        self._me = me
        self.chat = None
        self.input_chat = None

    async def get_chat(self):
        if not self.chat or not self.input_chat:
            chat = None
            
            async for dialog in self._client.iter_dialogs():
                if dialog.name == 'teagram-logs':
                    chat = dialog

                    break

            if not chat:
                self.chat = (
                    await create_group(
                        self._client,
                        'teagram-logs', 
                        'Here teagram logs',
                        megagroup=True
                    )
                ).__dict__["chats"][0].__dict__["id"]

                photo = InputChatUploadedPhoto(await self._client.upload_file(
                    file=BASE_PATH / 'assets' / 'channel_avatar.png'
                    )
                )
                
                await self._client(
                    EditPhotoRequest(
                        self.chat, photo
                    )
                )

                await self.get_chat()
            else:
                self.chat = chat.entity.id
                self.input_chat = chat.id

        return self.chat

    async def send_data(self, message: Union[types.Message, str]):
        """Send data to the chat."""
        return (
            await self._client.send_message(
                self.chat, message, parse_mode='HTML'
            )
            if isinstance(message, str)
            else await self._client.forward_messages(self.chat, message)
        )

    async def get_data(self, message_id: int):
        """Retrieve data using a message ID."""
        return await self._client.get_messages(
            self.chat, message_id
        )
