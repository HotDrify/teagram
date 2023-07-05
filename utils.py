"""
тут находится методы для работы с тг протоколм

    """

import asyncio
import functools
import random
import string
from types import FunctionType
from typing import Any, List, Literal, Tuple, Union

from pyrogram.file_id import PHOTO_TYPES, FileId
from pyrogram.types import Chat, Message, User

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

def get_color(user_id):
    """Возвращает цвет имени пользователя в Telegram.

    Параметры:
        user_id (int): Идентификатор пользователя.

    """
    colors_list = ["red (orange)", "orange", "violet", "green", "cyan", "blue", "pink"]
    name_color = colors_list[user_id % 7]

    return name_color

def get_raw(api_method: str, params: Dict) -> Dict:
    """Получает JSON-ответ от Telegram API

    Параметры:
        api_method (str): Метод API для вызова
        params (Dict): Параметры для запроса

    Возвращает:
        Dict: JSON-ответ от Telegram API
    """
    response = app.send(api_method, params).json
    return response

def get_all_users(client: Client, chat_id: int) -> List[User]:
    """Получает список всех пользователей, которые писали в указанный чат.

    Параметры:
        - client: объект Pyrogram API;
        - chat_id: идентификатор чата.

    Возвращает:
        - список пользователей типа List[User].
    """

    all_users = []

    for message in client.iter_history(chat_id, limit=None):
        user = message.from_user
        if user and user not in all_users:
            all_users.append(user)

    return all_users

def get_all_chats(client: Client) -> List[Chat]:
    """Получает список всех чатов, в которых состоит бот или пользователь.

    Параметры:
        - client: объект Pyrogram API.

    Возвращает:
        - список чатов типа List[Chat].
    """

    all_chats = []

    for dialog in client.iter_dialogs():
        all_chats.append(dialog.chat)

    return all_chats

def create_poll(
    chat_id: int,
    question: str,
    options: List[str],
) -> None:
    """Создает голосование в чате.

    Параметры:
        - chat_id: идентификатор чата;
        - question: текст вопроса в голосовании;
        - options: список вариантов ответа в голосовании.

    Возвращает:
        - Ничего не возвращает.
    """
    with client:
        client.send_poll(
            chat_id=chat_id,
            question=question,
            options=options
        )