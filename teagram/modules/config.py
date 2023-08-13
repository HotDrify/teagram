from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQuery,
                            InlineQueryResultArticle, InputTextMessageContent,
                            Message)
from aiogram import Bot, Dispatcher

from pyrogram import Client, types
from .. import loader, utils

@loader.module(name="config", author="teagram", version=1)
class ConfigMod(loader.Module):
    """настройка модулей"""
    def __init__(self):
        self.inline_bot: Bot = self.bot.bot
        self._dp: Dispatcher = self.bot._dp

    @loader.on_bot(lambda _, __, call: call.data == "send_cfg")
    async def example_callback_handler(self, app: Client, call: CallbackQuery):
        if not (call.from_user.id == (await app.get_me()).id):
            return await call.answer('Ты не владелец')
        
        me = await app.get_me()

        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        modules = [mod.name for mod in self.all_modules.modules]

        for module in sorted(modules, key=len):
            inline_keyboard.add(InlineKeyboardButton(module, callback_data=module))

        await self.inline_bot.send_message(me.id, 'Чо', reply_markup=inline_keyboard)

        return await call.answer("В лс пришли подробности", show_alert=True)

    async def example_inline_handler(self, app: Client, inline_query: InlineQuery, args: str):                                                                          
        """Пример инлайн-команды. Использование: @bot example [аргументы]"""
        await self.new_method(inline_query, args)

    async def new_method(self, inline_query, args):
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(),
                    title="Конфиг модулей",
                    description="Нажми на меня!" + (
                        f" Аргументы: {args}" if args
                        else "Укажите агрументы"
                    ),
                    input_message_content=InputTextMessageContent("Настройка конфига"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(
                            "Настроить",
                            callback_data="send_cfg"
                        ) # type: ignore
                    )
                )
            ]
        )
# 
    async def config_cmd(self, app: Client, message: types.Message):
        """настройка"""
        bot = await self.inline_bot.get_me()
        await utils.answer_inline(message, bot.username, 'example')
            
