import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pyrogram import Client, types
from .. import loader, utils

@loader.module(name="config", author="teagram", version=1)
class ExampleMod(loader.Module):
    """настройка модулей"""
    async def config_cmd(self, app: Client, message: types.Message, args: str):
        """настройка"""
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        modules = [mod.name for mod in self.all_modules.modules]
        for module in modules:
            inline_keyboard.add(InlineKeyboardButton(module, callback_data=module))
        await message.reply("modules", reply_markup=inline_keyboard)