import logging
import inspect
import traceback
from aiogram.types import (
    CallbackQuery, Message, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, 
    InputTextMessageContent, InlineQueryResultPhoto, InlineQueryResultDocument)

from .types import Item
from .. import utils

class Events(Item):
    """
    Event handler class.
    Handles various event types such as messages, callback queries, and inline queries.
    """
    def __init__(self):
        super().__init__()
        self._units: dict

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
            return await message.reply_photo(
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
        if call.from_user.id != (await self._app.get_me()).id:
            await call.answer(
                "❌ Вы не владелец",
                cache_time=0
            )
            
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

                await self.bot.edit_message_text(
                    inline_message_id=call.inline_message_id,
                    text='✔ Вы изменили атрибут!',
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton('Вернуться', callback_data='send_cfg')
                    )
                )
        
        try:
            if call.data == 'teagram_perm_delete':
                call.data = '_loader_permdel'

            if (unit := self._units[call.data]):
                if unit.get('callback'):
                    if (
                        self._units.get('_loader_permdel', '') 
                        and 'teagram_perm_delete' in str(unit)
                    ):
                        self._units.pop(call.data)
                        from os import rmdir, remove

                        try:
                            remove(utils.BASE_PATH / 'config.ini')
                            remove(utils.BASE_PATH / 'db.json')

                            try:
                                rmdir(utils.BASE_PATH / 'teagram')
                            except:
                                pass

                            await call.answer('✔ Успешно...', True)
                        except PermissionError:
                            await call.answer('⚠ Недостаточно прав', True)
                        except FileNotFoundError:
                            await call.answer('⚠ Не удалось найти папку, удаляем сессию', True)
                        except:
                            await call.answer('⚠ Неизвестная ошибка, удаляем сессию', True)

                        await self._app.log_out()
                        return
                    
                    try:
                        await unit.callback(call)
                    except Exception as error:
                        logging.exception(error)
        except KeyError:
            pass

        for func in self._manager.callback_handlers.values():
            if not await self._check_filters(func, func.__self__, call):
                continue

            try:
                await func(call)
            except Exception as error:
                logging.exception(error)

        return call

    async def _inline_handler(self, inline_query: InlineQuery) -> InlineQuery:
        """
        Inline query event handler.

        Processes incoming inline queries by invoking appropriate inline handlers.

        Args:
            inline_query (InlineQuery): The incoming inline query.

        Returns:
            InlineQuery: The processed inline query.
        """
        if inline_query.from_user.id != (await self._app.get_me()).id:
            await inline_query.answer(
                    [
                        InlineQueryResultArticle(
                            id=utils.random_id(),
                            title="Teagram",
                            description='Вы не владелец',
                            input_message_content=InputTextMessageContent(
                                "❌ Вы не владелец")
                        )
                    ], cache_time=0
                )

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

        query_ = query.split()

        cmd = query_[0]
        args = " ".join(query_[1:])

        try:
            form = self._units[query]
            text = form.get('text')
            keyboard = form.get('keyboard')

            if not form['photo'] and not form['doc']:
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
            elif form['photo']:
                await inline_query.answer(
                    [
                        InlineQueryResultPhoto(
                            id=utils.random_id(),
                            title=form.get('title'),
                            description=form.get('description'),
                            input_message_content=InputTextMessageContent(
                                text,
                                parse_mode='HTML',
                                disable_web_page_preview=True
                            ),
                            reply_markup=keyboard,
                            photo_url=form['photo'],
                            thumb_url=form['photo']
                        )
                    ]
                )
            else:
                await inline_query.answer(
                    [
                        InlineQueryResultDocument(
                            id=utils.random_id(),
                            title=form.get('title'),
                            description=form.get('description'),
                            input_message_content=InputTextMessageContent(
                                text,
                                parse_mode='HTML',
                                disable_web_page_preview=True
                            ),
                            reply_markup=keyboard,
                            document_url=form['doc']
                        )
                    ]
                )
        except KeyError:
            pass
        except Exception as error:
            traceback.print_exc()

        try:    
            if (data := self.cfg[cmd]):
                if not args:
                    return await inline_query.answer(
                        [
                            InlineQueryResultArticle(
                                id=utils.random_id(),
                                title="Teagram",
                                description='Укажите значение',
                                input_message_content=InputTextMessageContent(
                                    "❌ Вы не указали значение")
                            )
                        ], cache_time=0
                    )
                attr = data['attr']
                data['toset'] = args

                await inline_query.answer(
                    [
                        InlineQueryResultArticle(
                            id=utils.random_id(),
                            title="☕ Teagram",
                            input_message_content=InputTextMessageContent(
                                "Вы уверены что хотите изменить атрибут?"),
                            reply_markup=InlineKeyboardMarkup()
                            .add(InlineKeyboardButton('✔ Подвердить', callback_data=f'cfgyes{cmd}|{attr}'))
                            .add(InlineKeyboardButton('❌ Отмена', callback_data='send_cfg'))
                        )
                    ], cache_time=0
                )
        except KeyError:
            pass

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
