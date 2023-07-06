import logging

from googletrans import Translator
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="Translator")
class TranslatorModule(loader.Module):
    """Используйте Google переводчик прямо через 🍵teagram!"""
    async def translate(self, app: Client, message: types.Message, args: str):
        await utils.answer(message, "☕")
        tr = Translator()
        translated = tr.translate(args[0], dest=args[1:])
        await utils.answer(
            message,
            f"""
🍵 `Teagram | UserBot`
Переведено с **{translated.src}** на **{translated.dest}**
**Перевод:**
`{translated.text}`
**Произношение:**
`{translated.pronunciation}`
            """
        )
