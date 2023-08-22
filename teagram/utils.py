import asyncio
import functools
import random
import string
import typing
import yaml
import os
import contextlib
import aiohttp
from types import FunctionType
from typing import Any, List, Literal, Tuple, Union
from urllib.parse import urlparse

from pyrogram.file_id import PHOTO_TYPES, FileId
from telethon.types import Chat, User
from telethon import TelegramClient
from telethon.tl.custom import Message

from . import database


def get_full_command(message: Message) -> Union[
    Tuple[Literal[""], Literal[""], Literal[""]], Tuple[str, str, str]
]:
    """Вывести кортеж из префикса, команды и аргументов

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    message.text = str(message.text)
    prefixes = database.db.get("teagram.loader", "prefixes", ["."])

    for prefix in prefixes:
        if (
            message.text
            and len(message.text) > len(prefix)
            and message.text.startswith(prefix)
        ):
            command, *args = message.text[len(prefix):].split(maxsplit=1)
            break
    else:
        return "", "", ""

    return prefixes[0], command.lower(), args[-1] if args else ""


async def answer(
    message: Union[Message, List[Message]],
    response: Union[str, Any]
) -> List[Message]:
    messages: List[Message] = []

    if isinstance(message, list):
        message: Message = message[0]

    if isinstance(response, str):
        client: TelegramClient = message._client # type: ignore
        chat = message.chat

        try:
            msg = await client.edit_message(
                (chat.id if chat else None or message._chat_peer), # type: ignore
                message.id, # type: ignore
                response,
                parse_mode='html'
            )
        except:
            msg = await message.reply(response, parse_mode='html')
        
        messages.append(msg)

    return messages

def run_sync(func: FunctionType, *args, **kwargs) -> asyncio.Future:
    """Запускает асинхронно нон-асинк функцию

    Параметры:
        func (``types.FunctionType``):
            Функция для запуска

        args (``list``):
            Аргументы к функции

        kwargs (``dict``):
            Параметры к функции
    """
    return asyncio.get_event_loop().run_in_executor(
        None, functools.partial(
            func, *args, **kwargs)
    )

def get_ram() -> float:
    """Возвращает данные о памяти."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem = process.memory_info()[0] / 2.0**20
        for child in process.children(recursive=True):
            mem += child.memory_info()[0] / 2.0**20
        return round(mem, 1)
    except:
        return 0

def get_cpu() -> float:
    """Возвращает данные о процессоре."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        cpu = process.cpu_percent()
        for child in process.children(recursive=True):
            cpu += child.cpu_percent()
        return round(cpu, 1)
    except:
        return 0
    
def get_platform() -> str:
    """Возращает платформу."""
    IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
    IS_CODESPACES = "CODESPACES" in os.environ
    IS_DOCKER = "DOCKER" in os.environ
    IS_GOORM = "GOORM" in os.environ
    IS_WIN = "WINDIR" in os.environ
    IS_WSL = False
    
    with contextlib.suppress(Exception):
        from platform import uname
        if "microsoft-standard" in uname().release:
            IS_WSL = True

    if IS_TERMUX:
        platform = "<emoji id=5407025283456835913>📱</emoji> Termux"
    elif IS_DOCKER:
        platform = "<emoji id=5431815452437257407>🐳</emoji> Docker"
    elif IS_GOORM:
        platform = "<emoji id=5215584860063669771>💚</emoji> Goorm"
    elif IS_WSL:
        platform = "<emoji id=6327609909416298142>🧱</emoji> WSL"
    elif IS_WIN:
        platform = "<emoji id=5309880373126113150>💻</emoji> Windows"
    elif IS_CODESPACES:
        platform = "<emoji id=5467643451145199431>👨‍💻</emoji> Github Codespaces"
    else:
        platform = "🖥️ VDS"
    
    return platform

def random_id(length: int = 10) -> str:
    """Returns random id"""
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


def get_langpack() -> Union[Any, List]:
    if not (lang := database.db.get('teagram.loader', 'lang')):
        database.db.set('teagram.loader', 'lang', 'en')

        get_langpack()
    else:
        with open(f'teagram/langpacks/{lang}.yml') as file:
            pack = yaml.safe_load(file)

        return pack

async def paste_neko(code: str):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(
                "https://nekobin.com/api/documents",
                json={"content": code},
            ) as paste:
                paste.raise_for_status()
                result = await paste.json()
    except Exception:
        return "Pasting failed"
    else:
        return f"nekobin.com/{result['result']['key']}.py"
