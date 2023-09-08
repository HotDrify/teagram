import inspect
import logging

from aiogram.types import (CallbackQuery, InlineQuery,
                        InlineQueryResultArticle, InputTextMessageContent,
                        Message, InlineKeyboardButton, InlineKeyboardMarkup)

from .. import utils
from .types import Item


class Events(Item):
    """Обработчик событий"""

    async def _message_handler(self, message: Message) -> Message:
        """Обработчик сообщений"""
        if "/start" in message.text:
            await message.answer_photo(
                photo=open('assets/bot_avatar.png', 'rb'),
                caption='☕ Привет! Это модульный юзербот написанный на pyrogram!'
                '\n\n☕<a href="https://github.com/hotdrify/teagram">Github</a>'
                '\n🤔<a href="https://t.me/ubteagram">Поддержка</a>'
            )
        for func in self._all_modules.message_handlers.values():
            if not await self._check_filters(func, func.__self__, message):
                continue

            try:
                await func(self._app, message)
            except Exception as error:
                logging.exception(error)

        return message

    async def _callback_handler(self, call: CallbackQuery) -> CallbackQuery:
        """Обработчик каллбек-хендлеров"""
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
                
        for func in self._all_modules.callback_handlers.values():
            if not await self._check_filters(func, func.__self__, call):
                continue

            try:
                await func(self._app, call)
            except Exception as error:
                logging.exception(error)

        return call

    async def _inline_handler(self, inline_query: InlineQuery) -> InlineQuery:
        """Обработчик инлайн-хендеров"""
        if not (query := inline_query.query):
            commands = ""
            for command, func in self._all_modules.inline_handlers.items():
                if await self._check_filters(func, func.__self__, inline_query):
                    commands += f"\n💬 <code>@{(await self.bot.me).username} {command}</code>"

            message = InputTextMessageContent(
                f"👇 <b>Доступные команды</b>\n"
                f"{commands}"
            )

            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title="Доступные команды",
                        input_message_content=message,
#                        thumb_url="ссылку на фото",
                    )
                ], cache_time=0
            )

        query_ = query.split()

        cmd = query_[0]
        args = " ".join(query_[1:])

        try:
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
                else:
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
                                .add(InlineKeyboardButton('❌ Отмена', callback_data='send_cfg')) # type: ignore
                            )
                        ], cache_time=0
                    )
        except KeyError:
            pass

        func = self._all_modules.inline_handlers.get(cmd)
        if not func:
            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title="Ошибка",
                        input_message_content=InputTextMessageContent(
                            "❌ Такой инлайн-команды нет")
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
                await func(self._app, inline_query, args)
            else:
                await func(self._app, inline_query)
        except Exception as error:
            logging.exception(error)

        return inline_query
