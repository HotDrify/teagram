import asyncio
import functools
import random
import string
import yaml
import os
from types import FunctionType
from typing import Any, List, Literal, Tuple, Union

from pyrogram.file_id import PHOTO_TYPES, FileId
from pyrogram.types import Chat, Message, User
from pyrogram import Client

from . import database


def get_full_command(message: Message) -> Union[
    Tuple[Literal[""], Literal[""], Literal[""]], Tuple[str, str, str]
]:
    """Вывести кортеж из префикса, команды и аргументов

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    message.text = str(message.text or message.caption)
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
    response: Union[str, Any],
    chat_id: Union[str, int] = None,
    doc: bool = False,
    photo: bool = False,
    **kwargs
) -> List[Message]:
    """В основном это обычный message.edit, но:
        - Если содержание сообщения будет больше лимита (4096 символов),
            то отправится несколько разделённых сообщений
        - Работает message.reply, если команду вызвал не владелец аккаунта

    Параметры:
        message (``pyrogram.types.Message`` | ``typing.List[pyrogram.types.Message]``):
            Сообщение

        response (``str`` | ``typing.Any``):
            Текст или объект которое нужно отправить

        chat_id (``str`` | ``int``, optional):
            Чат, в который нужно отправить сообщение

        doc/photo (``bool``, optional):
            Если ``True``, сообщение будет отправлено как документ/фото или по ссылке

        kwargs (``dict``, optional):
            Параметры отправки сообщения
    """
    messages: List[Message] = []

    if isinstance(message, list):
        message = message[0]

    if isinstance(response, str) and all(not arg for arg in [doc, photo]):
        outputs = [
            response[i: i + 4096]
            for i in range(0, len(response), 4096)
        ]

        if chat_id:
            messages.append(
                await message._client.send_message(
                    chat_id, outputs[0], **kwargs)
            )
        else:
            messages.append(
                await (
                    message.edit if message.outgoing
                    else message.reply
                )(outputs[0], **kwargs)
            )

        for output in outputs[1:]:
            messages.append(
                await messages[0].reply(output, **kwargs)
            )

    elif doc:
        if chat_id:
            messages.append(
                await message._client.send_document(
                    chat_id, response, **kwargs)
            )
        else:
            messages.append(
                await message.reply_document(response, **kwargs)
            )

    elif photo:
        if chat_id:
            messages.append(
                await message._client.send_photo(
                    chat_id, response, **kwargs)
            )
        else:
            messages.append(
                await message.reply_photo(response, **kwargs)
            )

    return messages

async def answer_inline(
    message: Union[Message, List[Message]],
    bot: Union[str, int],
    query: str,
    chat_id: Union[str, int] = ''
) -> None:
    """
    Параметры:
        message (``pyrogram.types.Message`` | ``typing.List[pyrogram.types.Message]``):
            Сообщение

        bot (``str`` | ``int``):
            Ник или аиди инлайн бота
        
        query (``str``):
            Параметры для инлайн бота

        chat_id (``str`` | ``int``, optional):
            Чат, в который нужно отправить результат инлайна
    """

    if isinstance(message, list):
        message = message[0]

    app: Client = message._client
    message: Message

    results = await app.get_inline_bot_results(bot, query)
    
    await app.send_inline_bot_result(
        chat_id or message.chat.id,
        results.query_id,
        results.results[0].id
    )

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


def get_message_media(message: Message) -> Union[str, None]:
    """Получить медиа с сообщения, если есть

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    return getattr(message, message.media or "", None)


def get_media_ext(message: Message) -> Union[str, None]:
    """Получить расширение файла

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    if not (media := get_message_media(message)):
        return None

    media_mime_type = getattr(media, "mime_type", "")
    extension = message._client.mimetypes.guess_extension(media_mime_type)

    if not extension:
        extension = ".unknown"
        file_type = FileId.decode(
            media.file_id).file_type

        if file_type in PHOTO_TYPES:
            extension = ".jpg"

    return extension


def get_display_name(entity: Union[User, Chat]) -> str:
    """Получить отображаемое имя

    Параметры:
        entity (``pyrogram.types.User`` | ``pyrogram.types.Chat``):
            Сущность, для которой нужно получить отображаемое имя
    """
    return getattr(entity, "title", None) or (
        entity.first_name or "" + (
            " " + entity.last_name
            if entity.last_name else ""
        )
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

def random_id(size: int = 10) -> str:
    """Возвращает рандомный идентификатор заданной длины

    Параметры:
        size (``int``, optional):
            Длина идентификатора
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(size)
    )


def get_langpack() -> Union[Any, List]:
    if not (lang := database.db.get('teagram.loader', 'lang')):
        database.db.set('teagram.loader', 'lang', 'en')

        get_langpack()
    else:
        with open(f'teagram/langpacks/{lang}.yml') as file:
            pack = yaml.safe_load(file)

        return pack