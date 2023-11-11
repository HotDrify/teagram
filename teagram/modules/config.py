#                            ██╗████████╗███████╗██╗░░░░░░█████╗░██╗░░░██╗███████╗
#                            ██║╚══██╔══╝╚════██║██║░░░░░██╔══██╗╚██╗░██╔╝╚════██║
#                            ██║░░░██║░░░░░███╔═╝██║░░░░░███████║░╚████╔╝░░░███╔═╝
#                            ██║░░░██║░░░██╔══╝░░██║░░░░░██╔══██║░░╚██╔╝░░██╔══╝░░
#                            ██║░░░██║░░░███████╗███████╗██║░░██║░░░██║░░░███████╗
#                            ╚═╝░░░╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
#                                            https://t.me/itzlayz
#                           
#                                    🔒 Licensed under the GNU AGPLv3
#                                 https://www.gnu.org/licenses/agpl-3.0.html

from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent
)
from inspect import getmembers, isroutine
from telethon import types

from .. import loader, utils, database
from ..types import Config
from ..utils import escape_html

import typing

@loader.module(name="config", author="teagram", version=1)
class ConfigMod(loader.Module):
    """Настройка модулей"""
    strings = {'name': 'config'}

    def __init__(self):
        self.inline_bot = self.bot.bot
        self._dp = self.bot._dp
        self.DEFAULT_ATTRS = [
            'manager', 'author', 'bot', 'callback_handlers',
            'command_handlers', 'inline_handlers', 'bot_username',
            'message_handlers', 'name', 'version', 'watcher_handlers',
            'boot_time', 'client', '_client', 'loops',
            'translator', 'logger', 'prefix', 'inline'
        ]
        self.config = None  # Пoявляется после get_attrs
        self.pending = False
        self.pending_id = utils.random_id(50)
        self.pending_module = False

        self.message = None
        self.chat = None
        self._def = False
        self.me = self.client._self_id
        self.bbot = None

    def validate(self, attribute):
        if isinstance(attribute, str):
            try:
                attribute = int(attribute)
            except:
                try:
                    attribute = bool(utils.strtobool(attribute))
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

            if isinstance(attrs[0][1], (ConfigMod, loader.ModuleConfig)):
                return attrs[0][1]
            else:
                for attr in attrs:
                    _attr = getattr(module, attr[0])

                    if isinstance(_attr, (ConfigMod, loader.ModuleConfig)):
                        return _attr

        return []


    @loader.on_bot(lambda _, call: call.data == "send_cfg")
    async def config_callback_handler(self, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer(self.strings['noowner'])

        inline_keyboard = InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
        modules = list(self.manager.modules)

        await self.inline_bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text='☕ <b>Teagram modules | Config</b> ',
            reply_markup=inline_keyboard,
            parse_mode='HTML'
        )

        if self.pending:
            self.pending, self.pending_id, self.pending_module = False, utils.random_id(50), False

        count = 1
        buttons = []

        for module in sorted(modules, key=lambda x: len(str(x))):
            name = module.name
            attrs = self.get_attrs(self.lookup(name))

            if not attrs:
                continue

            if 'config' in name.lower():
                continue

            data = f'mod_{name}|{call.inline_message_id}'
            buttons.append(InlineKeyboardButton(name, callback_data=str(data)))

            if count % 3 == 0:
                inline_keyboard.row(*buttons)
                buttons.clear()

            count += 1

        if buttons:
            inline_keyboard.row(*buttons)

        await self.inline_bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text='☕ <b>Teagram modules | Config</b> ',
            reply_markup=inline_keyboard,
            parse_mode='HTML'
        )

    @loader.on_bot(lambda _, call: call.data.startswith('mod'))
    async def answer_callback_handler(self, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer(self.strings['noowner'])

        data = call.data

        keyboard = InlineKeyboardMarkup()
        mod = self.lookup(data)
        attrs = self.get_attrs(mod)

        buttons = []
        for count, name in enumerate(attrs, start=1):
            _data = f'chattr{mod.name.split(".")[-1]}#{name}'

            buttons.append(
                InlineKeyboardButton(
                    name, 
                    callback_data=_data
                )
            )

            if count % 3 == 0:
                keyboard.row(*buttons)
                buttons.clear()

        if buttons:
            keyboard.row(*buttons)

        keyboard.add(InlineKeyboardButton(self.strings['back'], callback_data='send_cfg'))
        attributes = []

        for key, value in attrs.items():
            formated = str(value)
            if isinstance(value, tuple):
                formated = ', '.join(f"{k}: {v}" for k, v in value)

            attributes.append(f'➡ <i>{type(value).__name__}</i> <b>{key}</b>: <code>{formated or self.strings["nospec"]}</code>')

        attributes_text = '\n'.join(attributes)
        await self.inline_bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=f'<b>⚙ {mod.name}</b>\n\n{attributes_text}',
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    @loader.on_bot(lambda _, call: call.data.startswith('chattr'))
    async def change_attribute_callback_handler(self, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer(self.strings['noowner'])

        data = call.data.replace('chattr', '').split('#')
        module = data[0]
        attribute = data[1]

        module = self.lookup(module)
        cfg = self.get_attrs(module)
        value = cfg.get(attribute)

        docs = cfg.get_doc(attribute)
        default = cfg.get_default(attribute)

        self.config = self.get_attrs(module)
        self.pending = attribute
        self.pending_module = module
        self.pending_id = utils.random_id(3).lower()

        attrs = getmembers(self.pending_module, lambda a: not isroutine(a))
        attrs = [
            (key, value) for key, value in attrs if not (
                key.startswith('__') and key.endswith('__')
            ) and key not in self.DEFAULT_ATTRS
        ]

        for _attr in attrs:
            a = getattr(self.pending_module, _attr[0])
            if isinstance(a, Config) or isinstance(a, loader.ModuleConfig):
                self.modconfig = a
                break

        self.bot.cfg[self.pending_id] = {
            'cfg': self.config, 
            'attr': attribute, 
            'mod': module, 
            'modcfg': getattr(self.pending_module, _attr[0])
        }

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(
                '✒ '+self.strings['ch'],
                switch_inline_query_current_chat=f'{self.pending_id} '
            ),
            InlineKeyboardButton(
                '↪ '+self.strings['def'],
                callback_data='change_def'
            ),
            InlineKeyboardButton(
                self.strings['back'],
                callback_data='send_cfg'
            ),
        )

        if isinstance(docs, typing.Callable):
            docs = docs()

        text = (
            f'⚙ <b>{self.pending_module.name}</b>\n'
            f'➡ <b>{escape_html(self.strings["attr"])}</b>: <code>{escape_html(attribute)}</code>\n'
            f'➡ <b>{escape_html(self.strings["value"])}</b>: <code>{escape_html(value) or self.strings["nospec"]}</code>\n'
            f'↪ <b>{escape_html(self.strings["def"])}</b>: <code>{escape_html(default) or self.strings["nospec"]}</code>\n\n'+
            (f'❔ <code>{escape_html(docs)}</code>' if docs else "")
        )

        await self.inline_bot.edit_message_text(
            text,
            reply_markup=keyboard,
            inline_message_id=call.inline_message_id
        )

    @loader.on_bot(lambda _, call: call.data.startswith('change'))
    async def _change_callback_handler(self, call: CallbackQuery):
        if call.from_user.id != self.me:
            return await call.answer(self.strings['noowner'])
        
        if 'def' in call.data:
            attr = self.config.get_default(self.pending)
            
            self.config[self.pending] = attr
            self.config_db.set(
                self.pending_module.__class__.__name__.replace('Mod', ''),
                self.pending,
                attr
            )

            self.pending, self.pending_id, self.pending_module = False, utils.random_id(50), False
            self._def = False

            await call.answer(self.strings['chdef'])

    @loader.on_bot(lambda _, call: call.data.startswith('cfg'))
    async def cfg_callback_handler(self, call):
        if call.data.startswith('cfg'):
            if (attr := call.data.replace('cfgyes', '')):
                attr = attr.split('|')
                data = self.inline.cfg[attr[0]]
                validator = data['modcfg'].config.get(attr[1]).validator

                mark = ''
                if getattr(validator.type, 'keywords', ''):
                    try:
                        if validator:
                            validator._valid(data['toset'], **validator.type.keywords)
                        else:
                            mark += "\n⚠ <i>No validator</i>"
                    except Exception as error:
                        keywords = ""
                        for k, v in validator.type.keywords.items():
                            keywords += f"\n{k}: {v}"

                        return await self.bot.bot.edit_message_text(
                            inline_message_id=call.inline_message_id,
                            text=f'❌ <b>{error}\nAttribute keywords:</b> {keywords}',
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton(self.strings('back'), callback_data='send_cfg')
                            )
                        )
                
                data['cfg'][attr[1]] = utils.validate(data['toset'])
                data['modcfg'][attr[1]] = utils.validate(data['toset'])
                self.config.config[attr[1]].value = utils.validate(data['toset'])

                self.db.set(
                    data['mod'].__class__.__name__,
                    attr[1],
                    utils.validate(data['toset'])
                )

                await self.bot.bot.edit_message_text(
                    inline_message_id=call.inline_message_id,
                    text=self.strings("chvalue") + mark,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(self.strings('back'), callback_data='send_cfg')
                    ),
                    parse_mode='html'
                )

    async def changing_inline_handler(self, inline_query, args):
        try:    
            cmd = inline_query.query.split()[0]

            if (data := self.inline.cfg[cmd]):
                if not args:
                    return await inline_query.answer(
                        [
                            InlineQueryResultArticle(
                                id=utils.random_id(),
                                title="Teagram",
                                description=self.strings("specvalue"),
                                input_message_content=InputTextMessageContent(
                                    self.strings("errvalue"))
                            )
                        ], cache_time=0
                    )
                attr = data['attr']
                data['toset'] = args
                attr = data['attr']
                data['toset'] = args

                await inline_query.answer(
                    [
                        InlineQueryResultArticle(
                            id=utils.random_id(),
                            title="☕ Teagram",
                            input_message_content=InputTextMessageContent(
                                self.strings("sure")),
                            reply_markup=InlineKeyboardMarkup()
                            .add(InlineKeyboardButton(self.strings("confirm"), callback_data=f'cfgyes{cmd}|{attr}'))
                            .add(InlineKeyboardButton(self.strings("decline"), callback_data='send_cfg'))
                        )
                    ], cache_time=0
                )
                await inline_query.answer(
                    [
                        InlineQueryResultArticle(
                            id=utils.random_id(),
                            title="☕ Teagram",
                            input_message_content=InputTextMessageContent(
                                self.strings("sure")),
                            reply_markup=InlineKeyboardMarkup()
                            .add(InlineKeyboardButton(self.strings("confirm"), callback_data=f'cfgyes{cmd}|{attr}'))
                            .add(InlineKeyboardButton(self.strings("decline"), callback_data='send_cfg'))
                        )
                    ], cache_time=0
                )
        except KeyError:
            pass

    async def cfg_inline_handler(self, inline_query: InlineQuery):
        if inline_query.from_user.id == self.me:
            await self.set_cfg(inline_query)

    async def set_cfg(self, inline_query):
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(),
                    title="Modules's config",
                    input_message_content=InputTextMessageContent(f"⚙ <b>{self.strings['cfg']}...</b>", 'html'),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("🔑 "+self.strings['cfg'], callback_data="send_cfg")
                    )
                )
            ]
        )

    async def config_cmd(self, message: types.Message):
        """Настройка через inline"""
        if not self.bbot:
            self.bbot = await self.inline_bot.get_me()

        bot = self.bbot
        await utils.invoke_inline(message, bot.username, 'cfg')
        await message.delete()
