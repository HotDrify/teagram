from types import FunctionType
from typing import Any, Dict, List, Union

from telethon import TelegramClient, types

from . import database, bot
from  dataclasses import dataclass, field
from .validators import Integer, String, Boolean, ValidationError

from aiogram import Dispatcher

class Module:
    """Module's descripton"""
    name: str
    author: str
    version: Union[int, float]

    async def on_load(self, app: TelegramClient) -> Any:
        """Invokes on module load"""


class ModulesManager:
    """Manager of modules"""

    def __init__(self) -> None:
        self.modules: List[Module]
        self.loops: List[FunctionType]
        self.watcher_handlers: List[FunctionType]

        self.command_handlers: Dict[str, FunctionType]
        self.message_handlers: Dict[str, FunctionType]
        self.inline_handlers: Dict[str, FunctionType]
        self.callback_handlers: Dict[str, FunctionType]

        self.aliases: dict
        self._local_modules_path: str

        self._client: TelegramClient
        self._db: database.Database
        self.me: types.User

        self.dp: Dispatcher
        self.bot_manager: bot.BotManager

class WaitForDefault:
    pass

@dataclass
class ConfigValue:
    option: str 
    docstring: str = ''
    default: Any = None
    value: Any = field(default_factory=WaitForDefault)
    validator: Union[Integer, String, Boolean] = None

    def __post_init__(self):
        if isinstance(self.value, WaitForDefault) or not self.value:
            self.value = self.default

    def __setattr__(self, key: str, value: Any):
        if self.validator:
            try:
                value = self.validator._valid(value)
            except ValidationError:
                value = self.default

        if isinstance(value, (tuple, list, dict)):
            raise ValidationError('Неправильный тип (Проверьте типы валидаторов) / Invalid type (Check validator types)')

        object.__setattr__(self, key, value)

class Config(dict):
    def __init__(self,  *values: list[ConfigValue]):
        self.config = {config.option: config for config in values}

        super().__init__(
            {option: config.value for option, config in self.config.items()}
        )

    def get_default(self, key: str) -> str:
        return self.config[key].default

    def get_doc(self, key: str) -> Union[str, None]:
        return self.config[key].docstring

    def __getitem__(self, key: str) -> Any:
        try:
            return self.config[key].value
        except KeyError:
            return None 

    def reload(self):
        for key in self.config:
            super().__setitem__(key, self.config[key].value)

