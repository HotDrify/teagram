import logging

from googletrans import Translator
from googletrans.models import Translated
from pyrogram import Client, types

from .. import loader, utils

# не трогайте если команды не пофиксили

@loader.module(name="Translator")
class TranslatorMod(loader.Module):
    """Используйте Google переводчик прямо через 🍵teagram!"""

    async def translate_cmd(self, app: Client, message: types.Message, args: str):
        await utils.answer(message, "☕")
        
        text = message.text.split(' ')
        translated: Translated = Translator().translate(text=' '.join(text[2:]), dest=str(text[1]))

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
