import logging

from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from .types import Item
from .. import utils

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
        if message.text == '/start':
            await message.reply_photo(
                photo='https://github.com/itzlayz/teagram-tl/blob/main/assets/bot_avatar.png?raw=true',
                caption='☕ Добро пожаловать! Это инлайн бот <b>Teagram</b>\n'
                '✒ Предлагаем вам настроить конфиг\n'
                '✒ Используйте инлайн команду <b>префикс</b><code>config</code>',
                parse_mode='html'
            )

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
        if call.data.startswith('cfg'):
            if (attr := call.data.replace('cfgyes', '')):
                attr = attr.split('|')
                data = self.cfg[attr[0]]
                data['cfg'][attr[1]] = utils.validate(data['toset'])

                self._db.set(
                    data['mod'].name,
                    attr[1],
                    utils.validate(data['toset'])
                )

                await self.bot.edit_message_text(inline_message_id=call.inline_message_id,
                                                 text='✔ Вы изменили атрибут!',
                                                 reply_markup=InlineKeyboardMarkup().add(
                                                     InlineKeyboardButton('Вернуться', callback_data='send_cfg')
                                                 ))

        for func in self._manager.callback_handlers.values():
            if not await self._check_filters(func, func.__self__, call):
                continue

            try:
                await func(call)
            except Exception as error:
                logging.exception(error)

        return call