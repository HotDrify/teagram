import logging
import asyncio
import sys
import traceback
import typing

from aiogram import Bot, Dispatcher, exceptions
from aiogram.types import (
    InlineKeyboardMarkup
)

from telethon.types import Message, Photo, Document
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import StartBotRequest
from telethon.tl.functions.contacts import UnblockRequest

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

    def __init__(self, app: TelegramClient, db: database.Database, manager: types.ModulesManager) -> None:
        """
        Initialize the Bot Manager.

        Parameters:
            app (TelegramClient): The client instance.
            db (database.Database): The database instance.
            manager (types.ModulesManager): The modules manager.
        """
        self._app = app
        self._db = db
        self._manager = manager

        self._token = self._db.get("teagram.bot", "token", None)
        self._units = {}
        self.cfg = {}

    async def load(self) -> Union[bool, NoReturn]:
        """
        Load the bot manager.

        Returns:
            Union[bool, NoReturn]: True if loaded successfully, else exits with an error.
        """
        logging.info("Loading bot manager...")
        error_text = "The userbot requires a bot. Resolve the bot creation issue and restart the userbot."

        new = False
        revoke = False

        if not self._token:
            self._token = await self._revoke_token()
            new = True
            revoke = True

        if not self._token:
            new = True


            self._token = await self._create_bot()
        if not self._token:
            logging.error(error_text)
            sys.exit(1)

        try:
            self.bot = Bot(self._token, parse_mode="html")
        except (exceptions.ValidationError, exceptions.Unauthorized):
            logging.error("Invalid token. Attempting to recreate the token.")

            result = await self._revoke_token()
            new = True
            revoke = True

            if not result:
                self._token = await self._create_bot() or logging.error(error_text) or sys.exit(1)
            else:
                self._token = result

        if new:
            name = (await self.bot.get_me()).username
            await self._app(StartBotRequest(name, name, 'start'))

            if revoke:
                async with self._app.converstaion("@BotFather") as conv:
                    try:
                        await conv.send_message("/cancel")
                    except errors.UserIsBlockedError:
                        await self._app(UnblockRequest('@BotFather'))

                    await conv.send_message("/setinline")
                    await conv.get_response()

                    await conv.send_message(self.bot_username)
                    await conv.get_response()

                    await conv.send_message("~teagram~ $")
                    await conv.get_response()

                    logger.success("Bot revoked successfully")

        self._db.set('teagram.bot', 'token', self._token)
        self._dp = Dispatcher(self.bot)
        self._register_handlers()

        asyncio.ensure_future(self._dp.start_polling())

        self.bot.manager = self
        return True

    def _register_handlers(self) -> None:
        """
        Register event handlers.
        """
        self._dp.register_message_handler(self._message_handler, lambda _: True, content_types=["any"])
        self._dp.register_inline_handler(self._inline_handler, lambda _: True)
        self._dp.register_callback_query_handler(self._callback_handler, lambda _: True)

    #     hikka compatibility
    async def invoke_unit(self, inline_id: str, message: Message) -> Message:
        return await utils.invoke_inline(
            message,
            (await self.bot.get_me()).username,
            inline_id
        )

    async def form(
        self,
        *,
        title: str,
        description: Union[str, None] = None,
        text: str,
        message: Message, 
        reply_markup: Union[InlineKeyboardMarkup, None] = None,
        callback: typing.Any = None,
        photo: Photo = None,
        doc: Document = None
    ):
        unit_id = callback or utils.random_id()
        self._units[unit_id] = {
            'type': 'form',
            'title': title,
            'description': description,
            'text': text,
            'keyboard': reply_markup,
            'callback': callback,
            'message': message,
            'photo': photo,
            'doc': doc,
            'top_msg_id': (
                (message.reply_to.reply_to_top_id or message.reply_to.reply_to_msg_id) 
                if message.reply_to else None
            )
        }

        try:
            await self.invoke_unit(unit_id, message)
        except Exception as error:
            del self._units[unit_id]

            error = "\n".join(traceback.format_exc().splitlines()[1:])

            await utils.answer(
                message,
                f"❌ <code>{error}</code>"
            )   

        return unit_id