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

    def __init__(self, app: TelegramClient, manager: "loader.ModulesManager") -> None:
        self.app = app
        self.manager = manager
    
    async def check_filters(
        self,
        func: FunctionType,
        message: Union[types.Message, Message],
        watcher: bool = False
    ) -> bool:
        """Проверка фильтров"""
        if (custom_filters := getattr(func, "_filters", None)):
            coro = custom_filters(message)
            if iscoroutine(coro):
                coro = await coro

            if not coro:
                return False
        else:
            _users = self.manager._db.get('teagram.loader', 'users', [])
            
            if not message.out and message.sender_id not in _users and not watcher:
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

        command = self.manager.aliases.get(command, command)
        func = self.manager.command_handlers.get(command.lower())
        if not func:
            return
    
        if not await self.check_filters(func, message):
            return
        
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
                self.manager.strings['errorcmd'].format(
                    message.text, error)
            )

        return message

    async def _handle_watchers(self, message: types.Message) -> types.Message:
        """Обработчик вотчеров"""
        for watcher in self.manager.watcher_handlers:
            try:
                if not await self.check_filters(watcher, message, True):
                    continue

                await watcher(message)
            except Exception as error:
                logging.exception(error)

        return message
