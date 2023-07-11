import logging
import re
from typing import Union

from loguru import logger
from pyrogram import errors, types

from .. import fsm, utils
from .types import Item


class TokenManager(Item):
    """Менеджер токенов"""

    async def _create_bot(self) -> Union[str, None]:
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
# надо аву поставить до папки teagram, нев ней а до нее

            await conv.ask("/setinline")
            await conv.get_response()

            await conv.ask("@" + bot_username)
            await conv.get_response()

            await conv.ask("teagram-команда")
            await conv.get_response()

            logger.success("Бот успешно создан")
            return token

    async def _revoke_token(self) -> str:
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

            for row in response.reply_markup.keyboard:
                for button in row:
                    search = re.search(r"@teagram_[0-9a-zA-Z]{6}_bot", button)
                    if search:
                        await conv.ask(button)
                        break
                else:
                    return logging.error("Нет созданного material бота")

            response = await conv.get_response()
            search = re.search(r"\d{1,}:[0-9a-zA-Z_-]{35}", response.text)

            logger.success("Бот успешно сброшен")
            return search.group(0)
