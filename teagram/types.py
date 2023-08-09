from types import FunctionType
from typing import Any, Dict, List, Union

from pyrogram import Client, types

from . import database


class Module:
    """Описание модуля"""
    name: str
    author: str
    version: Union[int, float]

    async def on_load(self, app: Client) -> Any:
        """Вызывается при загрузке модуля"""


class ModulesManager:
    """Менеджер модулей"""

    def __init__(self) -> None:
        self.modules: List[Module]
        self.watcher_handlers: List[FunctionType]

        self.command_handlers: Dict[str, FunctionType]
        self.message_handlers: Dict[str, FunctionType]
        self.inline_handlers: Dict[str, FunctionType]
        self.callback_handlers: Dict[str, FunctionType]

        self._local_modules_path: str

        self.me: types.User
        self._db: database.Database

        self.aliases: Dict[str, str]

        self.dp
        self.bot_manager
