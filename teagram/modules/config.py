from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    Message, ReplyKeyboardRemove
)
from aiogram import Bot, Dispatcher
from inspect import getmembers, isroutine
from pyrogram import Client, types

from .. import loader, utils


@loader.module(name="config", author="teagram", version=1)
class ConfigMod(loader.Module):
    """Настройка модулей"""

    def __init__(self):
        self.inline_bot: Bot = self.bot.bot
        self._dp: Dispatcher = self.bot._dp
        self.DEFAULT_ATTRS = [
            'all_modules', 'author', 'bot', 'callback_handlers',
            'command_handlers', 'db', 'inline_handlers',
            'message_handlers', 'name', 'version', 'watcher_handlers'
        ]

    def get_module(self, data):
        for module in self.all_modules.modules:
            if module.name.lower() in data.lower():
                return module

    def get_attrs(self, module):
        attrs = getmembers(module, lambda a: not isroutine(a))
        attrs = [
            a[0] for a in attrs if not (
                a[0].startswith('__') and a[0].endswith('__')
            ) and a[0] not in self.DEFAULT_ATTRS
        ]

        return attrs

    @loader.on_bot(lambda _, __, call: call.data == "send_cfg")  # type: ignore
    async def config_callback_handler(self, app: Client, call: CallbackQuery):
        if not (call.from_user.id == (await app.get_me()).id):
            return await call.answer('Ты не владелец')

        me = await app.get_me()

        inline_keyboard = InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
        modules = [mod for mod in self.all_modules.modules]
        message: Message = await self.inline_bot.send_message(
            me.id, 'Модули', reply_markup=inline_keyboard
        )

        count = 1

        buttons = []

        for module in modules:
            name = module.name

            if 'config' in name.lower():
                continue

            data = f'mod_{name}|{message.message_id}|{message.chat.id}'
            buttons.append(InlineKeyboardButton(
                name,
                callback_data=str(data)
            ))  # type: ignore

            if count % 3 == 0:
                inline_keyboard.row(*buttons)
                buttons.clear()

            count += 1

        if buttons:
            inline_keyboard.row(*buttons)

        await self.inline_bot.edit_message_reply_markup(
            message.chat.id,
            message.message_id,
            reply_markup=inline_keyboard
        )

    @loader.on_bot(lambda _, __, call: call.data.startswith('mod'))  # type: ignore
    async def answer_callback_handler(self, app: Client, call: CallbackQuery):
        data = call.data
        data_parts = data.split('|')
        message = int(data_parts[1])
        chat = int(data_parts[2])
        self.chat = chat
        self.message = message

        keyboard = InlineKeyboardMarkup()

        mod = self.get_module(data)
        attrs = self.get_attrs(mod)

        if not attrs:
            return await call.answer(
                'У этого модуля нету атрибутов',
                show_alert=True
            )

        buttons = []
        count = 1

        for attr in attrs:
            buttons.append(
                InlineKeyboardButton(
                    attr, callback_data=f'attr_{mod.name.split(".")[-1]}'  # type: ignore
                )
            )

            if count % 3 == 0:
                keyboard.row(*buttons)

            count += 1

        if buttons:
            keyboard.row(*buttons)

        keyboard.add(InlineKeyboardButton(
            '🔄 Назад',
            callback_data='send_cfg'
        )) # type: ignore

        await self.inline_bot.edit_message_text(
            f'Модуль: {mod.name}', self.chat, self.message
        )
        await self.inline_bot.edit_message_reply_markup(
            self.chat,
            self.message,
            reply_markup=keyboard
        )

    async def cfg_inline_handler(self, app: Client, inline_query: InlineQuery, args: str):
        if inline_query.from_user.id == (await app.get_me()).id:
            await self.set_cfg(inline_query)

    async def set_cfg(self, inline_query):
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(),
                    title="Конфиг модулей",
                    input_message_content=InputTextMessageContent("Настройка конфига"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            "Отправить конфиг",
                            callback_data="send_cfg"
                        )  # type: ignore
                    )
                )
            ]
        )

    async def config_cmd(self, app: Client, message: types.Message):
        """Настройка через inline"""

        bot = await self.inline_bot.get_me()
        await utils.answer_inline(message, bot.username, 'cfg')
