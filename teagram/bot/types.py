import logging
import inspect

from types import FunctionType
from typing import Union

from aiogram.types import CallbackQuery, InlineQuery, Message, InlineKeyboardMarkup
from telethon import TelegramClient

from .. import database, types
from .utils import Utils

logger = logging.getLogger()

class Item(Utils):
    """
    Base class for items.
    This class provides functionality for checking filters applied to event handlers.
    """

    def __init__(self) -> None:
        """
        Initialize the class.
        """
        self._manager: types.ModulesManager = None
        self._db: database.Database = None
        self._app: TelegramClient = None

    async def _check_filters(
        self,
        func: FunctionType,
        module: types.Module,
        update_type: Union[Message, InlineQuery, CallbackQuery],
    ) -> bool:
        """
        Check filters for an event handler.

        Args:
            func (FunctionType): The event handler function.
            module (types.Module): The module the function belongs to.
            update_type (Union[Message, InlineQuery, CallbackQuery]): The type of update.

        Returns:
            bool: True if the event should be processed, False otherwise.
        """
        if (custom_filters := getattr(func, "_filters", None)):
            coro = custom_filters(module, update_type)
            if inspect.iscoroutine(coro):
                coro = await coro

            if not coro:
                return False
        elif update_type.from_user.id != self._manager.me.id:
            if not getattr(func, 'inline_everyone', None):
                return False

        return True

class InlineCall(CallbackQuery):
    def __init__(
        self,
        call: CallbackQuery,
        manager: 'types.bot.BotManager'
    ):
        self.inline_message_id = None
        self.callback_query = call
        self._bot = manager.bot

        for orig in (
            'id',
            'from_user',
            'message',
            'inline_message_id',
            'chat_instance',
            'data'
        ):
            setattr(
                self,
                orig,
                getattr(call, orig, None)
            )

    async def edit(
        self,
        text: str,
        reply_markup: InlineKeyboardMarkup = None,
        inline_message_id: str = None
    ):
        try:
            return await self._bot.edit_message_text(
                text,
                inline_message_id=inline_message_id or self.inline_message_id,
                reply_markup=reply_markup
            )
        except Exception:
            logger.exception("Can't edit inline call")

    async def delete(self):
        try:
            if self.message.chat:
                return await self._bot.delete_message(
                    chat_id=self.message.chat.id,
                    message_id=self.message.message_id
                )

            return False
        except Exception:
            logger.exception("Can't delete inline call")