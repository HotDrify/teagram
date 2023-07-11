import logging
import re

from typing import Union

from loguru import logger
from pyrogram import errors, types
from aiogram.utils.exceptions import Unauthorized

from .. import fsm, utils
from .types import Item


class TokenManager(Item):
    """Менеджер токенов"""

    async def _create_bot(self) -> Union[str, bool, None]:
        """Создать и настроить бота"""
        logging.info("Начался процесс создания нового бота...")

        async with fsm.Conversation(self._app, "@BotFather", True) as conv:
            try:
                await conv.ask("/cancel")
            except errors.UserIsBlocked:
                await self._app.unblock_user("@BotFather")

            await conv.get_response()

            await conv.ask("/newbot")
            response = await conv.get_response()

            if not all(
                phrase not in response.text
                for phrase in ["That I cannot do.", "Sorry"]
            ):
                logging.error("Произошла ошибка при создании бота. Ответ @BotFather:")
                logging.error(response.text)
                return False

            await conv.ask(f"Teagram UserBot of {utils.get_display_name(self._all_modules.me)[:45]}")
            await conv.get_response()

            bot_username = f"teagram_{utils.random_id(6)}_bot"
            self._db.set('teagram.bot', 'name', bot_username)

            await conv.ask(bot_username)
            response = await conv.get_response()

            search = re.search(r"(?<=<code>)(.*?)(?=</code>)", response.text.html)
            if not search:
                logging.error("Произошла ошибка при создании бота. Ответ @BotFather:")
                return logging.error(response.text)

            token = search.group(0)

            await conv.ask("/setuserpic")
            await conv.get_response()

            await conv.ask("@" + bot_username)
            await conv.get_response()

            await conv.ask_media("bot_avatar.png", media_type="photo")
            await conv.get_response()
# надо аву поставить до папки teagram, не в ней а до нее

            await conv.ask("/setinline")
            await conv.get_response()

            await conv.ask("@" + bot_username)
            await conv.get_response()

            await conv.ask("teagram-команда")
            await conv.get_response()

            logger.success("Бот успешно создан")
            return token

    async def _revoke_token(self) -> Union[str, None]:
        """Сбросить токен бота"""
        async with fsm.Conversation(self._app, "@BotFather", True) as conv:
            try:
                await conv.ask("/cancel")
            except errors.UserIsBlocked:
                await self._app.unblock_user("@BotFather")

            await conv.get_response()

            await conv.ask("/revoke")
            response: types.Message = await conv.get_response()

            if "/newbot" in response.text:
                return logging.error("Нет созданных ботов")
            
            bot_username = ""

            try:
                token = self._db.get('teagram.bot', 'token')

                if isinstance(token, str):
                    return token
                else:
                    raise(Unauthorized)
            except:
                try:
                    bot_username = self._db.get('teagram.bot', 'name')
                except:
                    bot_username = f"teagram_{utils.random_id(6)}_bot"
                    self._db.set('teagram.bot', 'name', bot_username)

            message = await conv.ask(bot_username) # type: ignore
            text = message.text
            token = text.split()[-1]

            logger.success("Бот успешно сброшен")
            return token
