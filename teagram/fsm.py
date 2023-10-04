import asyncio
import logging
from types import TracebackType
from typing import List, Union
from telethon import TelegramClient, types

class Conversation:
    """
    Conversation with user/bot (`telethon.TelegramClient.conversation`)
    """

    def __init__(
        self,
        app: TelegramClient,
        chat_id: Union[str, int],
        purge: bool = False
    ) -> None:
        """
        :param app: Telegram client
        :param chat_id: Chat id
        :param purge: Delete messages after conversation 
        """
        self.app: TelegramClient = app
        self.chat_id = chat_id
        self.purge = purge
        self._id = app._self_id

        self.message_to_purge: List[types.Message] = []

    async def __aenter__(self) -> "Conversation":
        return self

    async def __aexit__(
        self,
        exc_type: type,
        exc_value: Exception,
        exc_traceback: TracebackType
    ) -> bool:
        if all(
            [exc_type, exc_value, exc_traceback]
        ):
            logging.exception(exc_value)
        else:
            if self.purge:
                await self._purge()

        return self.message_to_purge.clear()

    async def ask(self, text: str, *args, **kwargs) -> types.Message:
        """
        :param text: Message text
        :param args: args
        :param kwargs: kwargs
        :return: `types.Message`
        """
        message = await self.app.send_message(
            self.chat_id, text, *args, **kwargs)

        self.message_to_purge.append(message)
        return message

    async def ask_media(
        self,
        file_path: str,
        *args,
        **kwargs
    ) -> types.Message:
        """
        :param file_path: Path to file
        :param args: args
        :param kwargs: kwargs
        :return: `types.Message` 
        """

        message = await self.app.send_file(self.chat_id, file_path, *args, **kwargs)

        self.message_to_purge.append(message)
        return message

    async def get_response(
            self, 
            timeout: int = 30, 
            limit: int = 1
        ) -> list[types.Message]:
        """
        :param timeout: Time to wait response
        :param limit: Number of messages to be retrieved
        :return: List with `types.Message`
        """
        _responses = []
        responses = self.app.iter_messages(self.chat_id, limit=limit)
        async for response in responses:
            if int(response._sender_id) != self._id:
                timeout -= 1
                if timeout == 0:
                    raise RuntimeError("Timed out")

                await asyncio.sleep(1)
                responses = self.app.iter_messages(self.chat_id, limit=limit)

            _responses.append(response)
            self.message_to_purge.append(response)

        return list(set(responses))

    async def _purge(self) -> bool:
        """Deletes all conversation's messages"""
        for message in self.message_to_purge:
            await message.delete()

        return True
