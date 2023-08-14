from types import FunctionType
from typing import Any, Dict, List, Union, Callable

from pyrogram import Client, types

from . import database
from  dataclasses import dataclass, field
from .validators import Integer, String, Boolean, ValidationError

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

class WaitForDefault:
    pass

@dataclass
class ConfigValue:
    option: str 
    default: Any = None
    value: Any = field(default_factory=WaitForDefault)
    validator: Union[Integer, String, Boolean] = None
    
    def __post_init__(self):
        if isinstance(self.value, WaitForDefault):
            self.value = self.default

    def __setattr__(self, key: str, value: Any):
        if self.validator:
            try:
                self.validator._valid(value)
            except ValidationError:
                value = self.default
        
        if isinstance(value, tuple):
            raise ValidationError('Tuple (Check validator types)')

        object.__setattr__(self, key, value)

class Config(dict):
    def __init__(self, *values: list[ConfigValue]):
        self.config = {config.option: config for config in values}

        super().__init__(
            {option: config.value for option, config in self.config.items()}
        )

    def get_default(self, key: str) -> str:
        return self.config[key].default

    def __getitem__(self, key: str) -> Any:
        try:
            return self.config[key].value
        except KeyError:
            return None
        
    def reload(self):
        for key in self.config:
            super().__setitem__(key, self.config[key].value)

        