import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, exceptions
from telethon import TelegramClient
from telethon.types import Message

from typing import Union, NoReturn
from loguru import logger

from .events import Events
from .token_manager import TokenManager

from .. import database, __version__, types, utils


class BotManager(Events, TokenManager):
    """
    Bot Manager class.
    Manages the bot's functionalities.
    """

    def __init__(self, app: TelegramClient, db: database.Database, all_modules: types.ModulesManager) -> None:
        """
        Initialize the Bot Manager.

        Parameters:
            app (TelegramClient): The client instance.
            db (database.Database): The database instance.
            all_modules (types.ModulesManager): The modules manager.
        """
        self._app = app
        self._db = db
        self._all_modules = all_modules

        self._token = self._db.get("teagram.bot", "token", None)

    async def load(self) -> Union[bool, NoReturn]:
        """
        Load the bot manager.

        Returns:
            Union[bool, NoReturn]: True if loaded successfully, else exits with an error.
        """
        logging.info("Loading bot manager...")
        error_text = "The userbot requires a bot. Resolve the bot creation issue and restart the userbot."

        self._token = self._token or await self._create_bot()
        if self._token is False:
            logging.error(error_text)
            return sys.exit(1)

        try:
            self.bot = Bot(self._token, parse_mode="html")
        except (exceptions.ValidationError, exceptions.Unauthorized):
            logging.error("Invalid token. Attempting to recreate the token.")

            result = await self._revoke_token()
            if not result:
                self._token = await self._create_bot() or logging.error(error_text) or sys.exit(1)
            else:
                self._token = result

        self._dp = Dispatcher(self.bot)
        self._register_handlers()

        asyncio.ensure_future(self._dp.start_polling())

        self.bot.manager = self
        logger.success("Bot manager successfully loaded")
        return True

    def _register_handlers(self) -> None:
        """
        Register event handlers.
        """
        self._dp.register_message_handler(self._message_handler, lambda _: True, content_types=["any"])
        self._dp.register_inline_handler(self._inline_handler, lambda _: True)
        self._dp.register_callback_query_handler(self._callback_handler, lambda _: True)

    async def use_inline(self, inline_id: str, message: Message) -> Message:
        return await utils.invoke_inline(
            message,
            (await self.bot.get_me()).username,
            inline_id
        )