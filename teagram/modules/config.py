from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    Message
)
from inspect import getmembers, isroutine
from pyrogram import Client, types
from asyncio import sleep

from .. import loader, utils, database, validators
from ..types import Config

# distutils will be deleted in python 3.12
# distutils будет удалена в python 3.12
def strtobool(val):
    # distutils.util.strtobool
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))

@loader.module(name="config", author="teagram", version=1)
class ConfigMod(loader.Module):
    """Настройка модулей"""

    def __init__(self):
        self.inline_bot = self.bot.bot
        self._dp = self.bot._dp
        self.DEFAULT_ATTRS = [
            'all_modules', 'author', 'bot', 'callback_handlers',
            'command_handlers', 'inline_handlers', 'bot_username',
            'message_handlers', 'name', 'version', 'watcher_handlers',
            'boot_time'
        ]
        self.config = None  # Пoявляется после get_attrs
        self.pending = False
        self.pending_id = utils.random_id(50)
        self.pending_module = False

        self.bbot = None
        self.me = self.all_modules.me.id

    def get_module(self, data: str) -> loader.Module:
        return next((module for module in self.all_modules.modules if module.name.lower() in data.lower()), None)
    
    def validate(self, attribute):
        if isinstance(attribute, str):
            try:
                attribute = int(attribute)
            except:
                try:
                    attribute = bool(strtobool(attribute))
                except:
                    pass

        return attribute

    def get_attrs(self, module):
        attrs = getmembers(module, lambda a: not isroutine(a))
        attrs = [
            (key, value) for key, value in attrs if not (
                key.startswith('__') and key.endswith('__')
            ) and key not in self.DEFAULT_ATTRS
        ]
        if len(attrs) > 1:
            self.config = getattr(module, attrs[0][0])
            self.config_db: database.Database = attrs[1][1]

            return attrs[0][1]
        
        return []
        

    @loader.on_bot(lambda _, __, call: call.data == "send_cfg")
    async def config_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer('Ты не владелец')
        
        inline_keyboard = InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
        modules = [mod for mod in self.all_modules.modules]
        await self.inline_bot.edit_message_text(inline_message_id=call.inline_message_id,
                                                 text='Модули',
                                                   reply_markup=inline_keyboard)

        if self.pending:
            self.pending, self.pending_module, self.pending_id = False, utils.random_id(50), False

        count = 1
        buttons = []

        for module in modules:
            name = module.name
            mod = self.get_module(name)
            attrs = self.get_attrs(mod)

            if not attrs or not isinstance(attrs, Config):
                continue

            if 'config' in name.lower():
                continue

            data = f'mod_{name}'
            buttons.append(InlineKeyboardButton(name, callback_data=str(data)))

            if count % 3 == 0:
                inline_keyboard.row(*buttons)
                buttons.clear()

            count += 1

        if buttons:
            inline_keyboard.row(*buttons)

        await self.inline_bot.edit_message_text(inline_message_id=call.inline_message_id,
                                                 text='Модули',
                                                   reply_markup=inline_keyboard)

    @loader.on_bot(lambda _, __, call: call.data.startswith('mod'))
    async def answer_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer('Ты не владелец')
        
        data = call.data
        self.message = call.inline_message_id

        keyboard = InlineKeyboardMarkup()
        mod = self.get_module(data)
        attrs = self.get_attrs(mod)

        if not attrs:
            return await call.answer('У этого модуля нету атрибутов', show_alert=True)

        buttons = []
        count = 1

        for name in attrs:
            buttons.append(
                InlineKeyboardButton(
                    name, callback_data=f'ch_attr_{mod.name.split(".")[-1]}_{name}'
                )
            )

            if count % 3 == 0:
                keyboard.row(*buttons)
                buttons.clear()

            count += 1

        if buttons:
            keyboard.row(*buttons)

        keyboard.add(InlineKeyboardButton('🔄 Назад', callback_data='send_cfg'))
        
        attributes = []
        for key, value in attrs.items():
            formated = str(value)
            if isinstance(value, tuple):
                formated = ', '.join(f"{k}: {v}" for k, v in value)

            attributes.append(f'➡ <b>(Тип {type(value).__name__})</b> <b>{key}</b>: <code>{formated}</code>')

        attributes_text = '\n'.join(attributes)
        await self.inline_bot.edit_message_text(
            text=f'🆔 Модуль: {mod.name}\n\n{attributes_text}',
            inline_message_id=call.inline_message_id
        )
        
        await self.inline_bot.edit_message_reply_markup(inline_message_id=call.inline_message_id,
                                                         reply_markup=keyboard)

    @loader.on_bot(lambda _, __, call: call.data.startswith('ch_attr_'))
    async def change_attribute_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer('Ты не владелец')
        
        data = call.data.replace('ch_attr_', '').split('_')
        module = data[0]
        attribute = data[1]

        module = self.get_module(module)

        self.pending = attribute
        self.pending_module = module
        self.pending_id = utils.random_id(3).lower()
        self.bot.cfg[self.pending_id] = {'cfg': self.config, 'attr': attribute, 'mod': module}

        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton(
                '✒ Сменить атрибут',
                switch_inline_query_current_chat=self.pending_id + ' '
            ),
            InlineKeyboardButton(
                '↪ По умолчанию',
                callback_data='change_def'
            ),
            InlineKeyboardButton(
                '🔄 Назад',
                callback_data='send_cfg'
            ),
        )

        await self.inline_bot.edit_message_text(
            text=f'🆔 Модуль: <b>{self.pending_module.name}</b>\n➡ Атрибут: <b>{attribute}</b>',
            inline_message_id=self.message,
            reply_markup=keyboard
        )

    @loader.on_bot(lambda _, __, data: data.data == 'aaa')
    async def aaa_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer('Ты не владелец')
        
        await call.answer(f'Напишите "{self.pending_id} НОВЫЙ_АТРИБУТ"', show_alert=True)

    @loader.on_bot(lambda _, call: call.data.startswith('change'))
    async def _change_callback_handler(self, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer(self.strings['noowner'])
        
        if 'def' in call.data:
            attr = self.config.get_default(self.pending)

            self.config[self.pending] = attr
            self.config_db.set(
                self.pending_module.name,
                self.pending,
                attr
            )

            self.pending, self.pending_id, self.pending_module = False, utils.random_id(50), False
            self._def = False

            await call.answer('✔ Значение изменено по умолчанию')

    async def cfg_inline_handler(self, app: Client, inline_query: InlineQuery):
        if inline_query.from_user.id == self.me:
            await self.set_cfg(inline_query)

    async def set_cfg(self, inline_query):
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(),
                    title="Конфиг модулей",
                    input_message_content=InputTextMessageContent("Настройка конфига"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("Отправить конфиг", callback_data="send_cfg")
                    )
                )
            ]
        )

    async def config_cmd(self, app: Client, message: types.Message):
        """Настройка через inline"""
        bot = await self.inline_bot.get_me()
        if not self.bbot:
            self.bbot = bot.username

        await utils.answer_inline(message, self.bbot, 'cfg')

