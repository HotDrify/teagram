
import logging

from aiogram.types import CallbackQuery, Message

from .types import Item

class Events(Item):
    """
    Event handler class.
    Handles various event types such as messages, callback queries, and inline queries.
    """

    async def _message_handler(self, message: Message) -> Message:
        """
        Message event handler.

        Processes incoming messages by invoking appropriate message handlers.

        Args:
            message (Message): The incoming message.

        Returns:
            Message: The processed message.
        """
        for func in self._manager.message_handlers.values():
            if not await self._check_filters(func, func.__self__, message):
                continue

            try:
                await func(message)
            except Exception as error:
                logging.exception(error)

        return message

    async def _callback_handler(self, call: CallbackQuery) -> CallbackQuery:
        """
        Callback query event handler.

        Processes incoming callback queries by invoking appropriate callback handlers.

        Args:
            call (CallbackQuery): The incoming callback query.

        Returns:
            CallbackQuery: The processed callback query.
        """
        for func in self._manager.callback_handlers.values():
            if not await self._check_filters(func, func.__self__, call):
                continue

            try:
                await func(call)
            except Exception as error:
                logging.exception(error)

        return call