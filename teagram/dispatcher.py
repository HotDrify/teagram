import logging
from inspect import getfullargspec, iscoroutine
from types import FunctionType

from telethon import TelegramClient, types
from telethon.events import NewMessage, MessageEdited
from typing import Union
from telethon.tl.custom import Message

from . import loader, utils

import traceback

class DispatcherManager:
    """Менеджер диспетчера"""

    def __init__(self, app: TelegramClient, modules: "loader.ModulesManager") -> None:
        self.app = app
        self.modules = modules
    
    async def check_filters(
        self,
        func: FunctionType,
        message: Union[types.Message, Message]
    ) -> bool:
        """Проверка фильтров"""
        if (custom_filters := getattr(func, "_filters", None)):
            coro = custom_filters(message)
            if iscoroutine(coro):
                coro = await coro

            if not coro:
                return False
        else:
            _users = self.modules._db.get('teagram.loader', 'users', [])
            
            if not message.out and message.sender_id not in _users:
                return False

        return True

    async def load(self) -> bool:
        """Загружает менеджер диспетчера"""
        logging.info("Загрузка диспетчера...")

        self.app.add_event_handler(
            self._handle_message,
            NewMessage
        )
        self.app.add_event_handler(
            self._handle_message,
            MessageEdited
        )

        logging.info("Диспетчер успешно загружен")
        return True

    async def _handle_message(self, message: types.Message) -> types.Message:
        """Обработчик сообщений"""        
        await self._handle_watchers(message)

        prefix, command, args = utils.get_full_command(message)
        if not (command or args):
            return

        command = self.modules.aliases.get(command, command)
        func = self.modules.command_handlers.get(command.lower())
        if not func:
            return
    
        if not await self.check_filters(func, message):
            return
        
        setattr(message, '_client', self.app)
        
        try:
            if (
                len(vars_ := getfullargspec(func).args) > 2
                and vars_[2] == "args"
            ):
                await func(message, utils.get_full_command(message)[2])
            else:
                await func(message)
        except Exception as error:
            error = traceback.format_exc()

            logging.exception(error)
            await utils.answer(
                message,
                f"<b>❌ Произошла ошибка при выполнении команды:</b> <code>{message.text}</code>\n"
                f"<b>❔ Логи:</b>\n<code>{error}</code>"
            )

        return message

    async def _handle_watchers(self, message: types.Message) -> types.Message:
        """Обработчик вотчеров"""
        for watcher in self.modules.watcher_handlers:
            try:
                setattr(message, '_client', self.app)

                if not await self.check_filters(watcher, message):
                    continue

                await watcher(message)
            except Exception as error:
                logging.exception(error)

        return message
