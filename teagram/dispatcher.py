"""
тут находится диспечер

    """

import asyncio
import logging
from inspect import getfullargspec, iscoroutine
from types import FunctionType, TracebackType
from typing import List, Union

from pyrogram import Client, filters, types
from pyrogram.handlers import MessageHandler

from . import loader, utils


async def check_filters(func: FunctionType, app: Client, message: types.Message) -> bool:
    """Проверка фильтров"""
    if (custom_filters := getattr(func, "_filters", None)):
        coro = custom_filters(app, message)
        if iscoroutine(coro):
            coro = await coro

        if not coro:
            return False
    else:
        if not message.outgoing:
            return False

    return True

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
        responses = await self.app.get_history(self.chat_id, limit=1)
        while responses[0].from_user.is_self:
            timeout -= 1
            if not timeout:
                raise RuntimeError("Истекло время ожидания ответа")

            await asyncio.sleep(1)
            responses = await self.app.get_history(self.chat_id, limit=1)

        self.messagee_to_purge.append(responses[0])
        return responses[0]

    async def _purge(self) -> bool:
        """Удалить все отправленные и полученные сообщения"""
        for message in self.messagee_to_purge:
            await message.delete()

        return True

class DispatcherManager:
    """Менеджер диспетчера"""

    def __init__(self, app: Client, modules: "loader.ModulesManager") -> None:
        self.app = app
        self.modules = modules

    async def load(self) -> bool:
        """Загружает менеджер диспетчера"""
        logging.info("Загрузка диспетчера...")

        self.app.add_handler(
            MessageHandler(
                self._handle_message, filters.all)
        )

        logging.info("Диспетчер успешно загружен")
        return True

    async def _handle_message(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик сообщений"""
        await self._handle_watchers(app, message)
        await self._handle_other_handlers(app, message)

        prefix, command, args = utils.get_full_command(message)
        if not (command or args):
            return

        command = self.modules.aliases.get(command, command)
        func = self.modules.command_handlers.get(command.lower())
        if not func:
            return

        if not await check_filters(func, app, message):
            return

        try:
            if (
                len(vars_ := getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(app, message, utils.get_full_command(message)[2])
            else:
                await func(app, message)
        except Exception as error:
            logging.exception(error)
            await utils.answer(
                message, f"❌ Произошла ошибка при выполнении команды.\n"
                        f"Запрос был: <code>{message.text}</code>\n"
                        f"Подробности можно найти в <code>{prefix}logs</code>"
            )

        return message

    async def _handle_watchers(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик вотчеров"""
        for watcher in self.modules.watcher_handlers:
            try:
                if not await check_filters(watcher, app, message):
                    continue

                await watcher(app, message)
            except Exception as error:
                logging.exception(error)

        return message

    async def _handle_other_handlers(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик других хендлеров"""
        for handler in app.dispatcher.groups[0]:
            if getattr(handler.callback, "__func__", None) == DispatcherManager._handle_message:
                continue

            coro = handler.filters(app, message)
            if iscoroutine(coro):
                coro = await coro

            if not coro:
                continue

            try:
                handler = handler.callback(app, message)
                if iscoroutine(handler):
                    await handler
            except Exception as error:
                logging.exception(error)

        return message