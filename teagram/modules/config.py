from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    Message, ReplyKeyboardRemove
)
from aiogram import Bot, Dispatcher
from inspect import getmembers, isroutine
from pyrogram import Client, types
from asyncio import sleep

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
        self.pending = False
        self.pending_id = utils.random_id(50)
        self.pending_module = False

    def get_module(self, data: str) -> loader.Module:
        for module in self.all_modules.modules:
            if module.name.lower() in data.lower():
                return module

    def get_attrs(self, module):
        attrs = getmembers(module, lambda a: not isroutine(a))
        attrs = [
            a for a in attrs if not (
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

        if self.pending:
            self.pending, self.pending_module, self.pending_id = (False, utils.random_id(50), False)

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
            attr = attr[0]
            buttons.append(
                InlineKeyboardButton(
                    attr, callback_data=f'ch_attr_{mod.name.split(".")[-1]}_{attr}'  # type: ignore
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

        attributes = [f'<b>(Тип {type(attr[1]).__name__})</b> <b>{attr[0]}</b>: <code>{attr[1]}</code>' for attr in attrs]
        attributes = '\n'.join(attributes)

        await self.inline_bot.edit_message_text(
            f'Модуль: {mod.name}\n{attributes}', self.chat, self.message
        )
        await self.inline_bot.edit_message_reply_markup(
            self.chat,
            self.message,
            reply_markup=keyboard
        )
    
    @loader.on_bot(lambda _, __, call: call.data.startswith('ch_attr_')) # type: ignore
    async def change_attribute_callback_handler(self, app: Client, call: CallbackQuery):
        data = call.data.replace('ch_attr_', '').split('_')
        module = data[0]
        attribute = data[1] # атрибут

        module = self.get_module(module)

        self.pending = attribute
        self.pending_module = module
        self.pending_id = utils.random_id(3)

        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton(
                'Сменить атрибут',
                callback_data='aaa'
            ), # type: ignore
            InlineKeyboardButton(
                '🔄 Назад',
                callback_data='send_cfg'
            ), # type: ignore
        )

        await self.inline_bot.edit_message_reply_markup(
            self.chat,
            self.message,
            reply_markup=keyboard
        )


    @loader.on_bot(lambda _, __, data: data.data == 'aaa') # type: ignore
    async def aaa_callback_handler(self, app: Client, call: CallbackQuery):
        await call.answer(
            f'Напишите "{self.pending_id} НОВЫЙ_АТРИБУТ"',
            show_alert=True
        )    

    @loader.on_bot(lambda self, __, msg: len(self.pending_id) != 50) # type: ignore
    async def change_message_handler(self, app: Client, message: Message):
        if self.pending_id in message.text: # type: ignore
            attr = message.text.split()[1]

            await app.delete_messages(message.chat.id, message.message_id)

            setattr(self.pending_module, self.pending, attr) # type: ignore

            self.pending, self.pending_id, self.pending_module = (False, utils.random_id(50), False)

            message = await message.reply('✔ Атрибут успешно изменен!')

            await sleep(2)

            await message.delete()


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
