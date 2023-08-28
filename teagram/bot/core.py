import logging
import asyncio
import sys
import traceback
import inspect

from aiogram import Bot, Dispatcher, exceptions
from aiogram.types import InlineKeyboardMarkup, InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from telethon import TelegramClient
from telethon.types import Message
from telethon.tl.functions.messages import StartBotRequest

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

    async def load(self) -> Union[bool, NoReturn]:
        """
        Load the bot manager.

        Returns:
            Union[bool, NoReturn]: True if loaded successfully, else exits with an error.
        """
        logging.info("Loading bot manager...")
        error_text = "The userbot requires a bot. Resolve the bot creation issue and restart the userbot."

        new = False

        if not self._token:
            self._token = await self._revoke_token()
            new = True

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
            
            if not result:
                self._token = await self._create_bot() or logging.error(error_text) or sys.exit(1)
            else:
                self._token = result

        if new:
            name = (await self.bot.get_me()).username
            await self._app(StartBotRequest(name, name, 'start'))

        self._db.set('teagram.bot', 'token', self._token)
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

    async def invoke_inline(self, inline_id: str, message: Message) -> Message:
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
    ):
        unit_id = utils.random_id()
        self._units[unit_id] = {
            'type': 'form',
            'title': title,
            'description': description,
            'text': text,
            'keyboard': reply_markup,
            'message': message,
            'top_msg_id': message.reply_to.reply_to_top_id or message.reply_to.reply_to_msg_id
        }

        try:
            await self.invoke_inline(unit_id, message)
        except Exception as error:
            del self._units[unit_id]

            error = "\n".join(traceback.format_exc().splitlines()[1:])

            await utils.answer(
                message,
                f'Не удалось отправить форму\n'
                f"<code>{error}</code>"
            )
    
    async def _inline_handler(self, inline_query: InlineQuery) -> InlineQuery:
        """
        Inline query event handler.

        Processes incoming inline queries by invoking appropriate inline handlers.

        Args:
            inline_query (InlineQuery): The incoming inline query.

        Returns:
            InlineQuery: The processed inline query.
        """
        if not (query := inline_query.query):
            commands = ""
            for command, func in self._manager.inline_handlers.items():
                if await self._check_filters(func, func.__self__, inline_query):
                    commands += f"\n💬 <code>@{(await self.bot.me).username} {command}</code>"

            message = InputTextMessageContent(
                f"👇 <b>Available Commands</b>\n"
                f"{commands}"
            )

            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title="Available Commands",
                        input_message_content=message
                    )
                ], cache_time=0
            )
        
        try:
            form = self._units[query]
            text = form.get('text')
            keyboard = form.get('keyboard')

            await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title=form.get('title'),
                        description=form.get('description'),
                        input_message_content=InputTextMessageContent(
                            text,
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        ),
                        reply_markup=keyboard
                    )
                ]
            )
        except Exception as error:
            traceback.print_exc()

        query_ = query.split()

        cmd = query_[0]
        args = " ".join(query_[1:])

        func = self._manager.inline_handlers.get(cmd)
        if not func:
            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title="Error",
                        input_message_content=InputTextMessageContent(
                            "❌ No such inline command")
                    )
                ], cache_time=0
            )

        if not await self._check_filters(func, func.__self__, inline_query):
            return

        try:
            if (
                len(vars_ := inspect.getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(inline_query, args)
            else:
                await func(inline_query)
        except Exception as error:
            logging.exception(error)

        return inline_query
