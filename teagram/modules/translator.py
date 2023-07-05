import logging

from googletrans import Translator
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="Translator")
class Translator(loader.Module):
    """Используйте Google переводчик прямо через 🍵teagram!"""
    async def on_load(self, app: Client):
        logging.info(f"[INFO] 🍵 {self.name} loaded")

    async def translate(self, app: Client, message: types.Message, args: str):
        tr = Translator()
        translated = tr.translate(args[0], dest=args[1:])
        
        await utils.answer(
            message,
            f'Перевод с {translated.src} на {translated.dest}\nПеревод: {translated.text}\nПроизношение: {translated.pronunciation}'
        )