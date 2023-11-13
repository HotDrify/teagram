from datetime import datetime
from types import FunctionType
from typing import (
    Any, 
    Dict, 
    List, 
    Union, 
    Callable, 
    Awaitable, 
    Optional
)

from telethon import TelegramClient, types
from telethon.tl import types
from telethon.tl.custom import Message as TeleMessage

from . import database, bot
from  dataclasses import dataclass, field
from .validators import Integer, String, Boolean, ValidationError

from aiogram import Dispatcher
from ast import literal_eval

import asyncio
import inspect

class Module:
    """Module's descripton"""
    name: str
    author: str
    version: Union[int, float]

    async def on_load(self) -> Any:
        """Invokes on module load"""
    
    async def on_unload(self) -> Any:
        """Invokes on module unload"""


class ModulesManager:
    """Manager of modules"""

    def __init__(self) -> None:
        self.modules: List[Module] 
        self.watcher_handlers: List[FunctionType] 

        self.command_handlers: Dict[str, FunctionType] 
        self.message_handlers: Dict[str, FunctionType] 
        self.inline_handlers: Dict[str, FunctionType] 
        self.callback_handlers: Dict[str, FunctionType] 
        self.loops: List[FunctionType]

        self._local_modules_path: str

        self._client: TelegramClient
        self._db: database.Database
        self.me: types.User

        self.aliases: dict 
        self.strings: dict 
        self.translator
        self.core_modules: list

        self.dp
        self.bot_manager: bot.BotManager
        self.inline: bot.BotManager # same as bot_manager

class WaitForDefault:
    pass

@dataclass
class ConfigValue:
    option: str 
    doc: str = ''
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

@dataclass(repr=True)
class HikkaValue:
    option: str
    default: Any = None
    doc: Union[Callable[[], str], str] = None
    value: Any = field(default_factory=WaitForDefault)
    validator: validator = None

    def __post_init__(self):
        if isinstance(self.value, WaitForDefault):
            self.value = self.default

    def set_no_raise(self, value: Any) -> bool:
        """
        Sets the config value w/o ValidationError being raised
        Should not be used uninternally
        """
        return self.__setattr__("value", value, ignore_validation=True)

    def __setattr__(
        self,
        key: str,
        value: Any,
        *,
        ignore_validation: bool = False,
    ):
        if key == "value":
            try:
                value = literal_eval(value)
            except Exception:
                pass

            # Convert value to list if it's tuple just not to mess up
            # with json convertations
            if isinstance(value, (set, tuple)):
                value = list(value)

            if isinstance(value, list):
                value = [
                    item.strip() if isinstance(item, str) else item for item in value
                ]

            if self.validator:
                if value:
                    from . import validators

                    try:
                        value = self.validator._valid(value)
                    except validators.ValidationError as e:
                        if not ignore_validation:
                            raise e

                        value = self.default

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
        return self.config[key].doc

    def __getitem__(self, key: str) -> Any:
        try:
            return self.config[key].value
        except KeyError:
            return None 
        
    def reload(self):
        for key in self.config:
            super().__setitem__(key, self.config[key].value)

class Message(TeleMessage):
    """`telethon.tl.custom.Message`"""
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
    
    def __str__(self):
        return self.text
    
    def __invert__(self):
        return self.raw_text
    