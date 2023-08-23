import logging
from inspect import getfullargspec, iscoroutine
from types import FunctionType

from telethon import TelegramClient, types
from telethon.events import NewMessage
from typing import Union
from telethon.tl.custom import Message

from . import loader, utils


async def check_filters(
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
        if not message.out:
            return False

    return True


class DispatcherManager:
    """Менеджер диспетчера"""

    def __init__(self, app: TelegramClient, modules: "loader.ModulesManager") -> None:
        self.app = app
        self.modules = modules

    async def load(self) -> bool:
        """Загружает менеджер диспетчера"""
        self.owner = await self.app.get_me()
        logging.info("Загрузка диспетчера...")

        self.app.add_event_handler(
            self._handle_message,
            NewMessage
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
    
        if not await check_filters(func, app, message):
            return

        if message.from_id.user_id != self.owner.id:
            return
        
        message._client = self.app
        
        try:
            if (
                len(vars_ := getfullargspec(func).args) > 2
                and vars_[2] == "args"
            ):
                await func(message, utils.get_full_command(message)[2])
            else:
                await func(message)
        except Exception as error:
            logging.exception(error)
            await utils.answer(
                message,
                        f"❌ Произошла ошибка при выполнении команды.\n"
                        f"Запрос был: <code>{message.text}</code>\n"
                        f"Подробности можно найти в <code>{prefix}logs</code>"
            )

        return message

    async def _handle_watchers(self, message: types.Message) -> types.Message:
        """Обработчик вотчеров"""
        for watcher in self.modules.watcher_handlers:
            try:
                message._client = self.app
                
                if not await check_filters(watcher, message):
                    continue

                await watcher(message)
            except Exception as error:
                logging.exception(error)

        return message
