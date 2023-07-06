import asyncio
import logging
from types import TracebackType
from typing import List, Union

from pyrogram import Client, types


class Conversation:
    """Диалог с пользователем. Отправка сообщений и ожидание ответа"""

    def __init__(
        self,
        app: Client,
        chat_id: Union[str, int],
        purge: bool = False
    ) -> None:
        """Инициализация класса

        Параметры:
            app (``pyrogram.Client``):
                Клиент

            chat_id (``str`` | ``int``):
                Чат, в который нужно отправить сообщение

            purge (``bool``, optional):
                Удалять сообщения после завершения диалога
        """
        self.app = app
        self.chat_id = chat_id
        self.purge = purge

        self.messagee_to_purge: List[types.Message] = []

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

        return self.messagee_to_purge.clear()

    async def ask(self, text: str, *args, **kwargs) -> types.Message:
        """Отправить сообщение

        Параметры:
            text (``str``):
                Текст сообщения

            args (``list``, optional):
                Аргументы отправки сообщения

            kwargs (``dict``, optional):
                Параметры отправки сообщения
        """
        message = await self.app.send_message(
            self.chat_id, text, *args, **kwargs)

        self.messagee_to_purge.append(message)
        return message

    async def ask_media(
        self,
        file_path: str,
        media_type: str,
        *args,
        **kwargs
    ) -> types.Message:
        """Отправить файл

        Параметры:
            file_path (``str``):
                Ссылка или путь до файла

            media_type (``str``):
                Тип отправляемого медиа

            args (``list``, optional):
                Аргументы отправки сообщения

            kwargs (``dict``, optional):
                Параметры отправки сообщения
        """
        available_media = [
            "animation", "audio",
            "document", "photo",
            "sticker", "video",
            "video_note", "voice"
        ]
        if media_type not in available_media:
            raise TypeError("Такой тип медиа не поддерживается")

        message = await getattr(self.app, "send_" + media_type)(
            self.chat_id, file_path, *args, **kwargs)

        self.messagee_to_purge.append(message)
        return message

    async def get_response(self, timeout: int = 30) -> types.Message:
        """Возвращает ответ

        Параметр:
            timeout (``int``, optional):
                Время ожидания ответа
        """
        responses = self.app.get_chat_history(self.chat_id, limit=1)
        async for response in responses:
            if response.from_user.is_self:
                timeout -= 1
                if timeout == 0:
                    raise RuntimeError("Истекло время ожидания ответа")

                await asyncio.sleep(1)
                responses = self.app.get_chat_history(self.chat_id, limit=1)

        self.messagee_to_purge.append(response)
        return response


    async def _purge(self) -> bool:
        """Удалить все отправленные и полученные сообщения"""
        for message in self.messagee_to_purge:
            await message.delete()

        return True
