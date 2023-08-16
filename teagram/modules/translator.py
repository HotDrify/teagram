from .. import loader, utils, validators
from ..types import Config, ConfigValue

from pyrogram import types
from googletrans import Translator, LANGUAGES
from googletrans.models import Translated

@loader.module('Translator', 'teagram')
class TranslatorMod(loader.Module):
    """Переводчик"""
    
    def __init__(self):
        language = self.db.get('Translator', 'language')
        
        if language is None:
            language = 'en'

        self.config = Config(
            ConfigValue(
                'language',
                'en',
                language,
                validators.String()
            )
        )

    async def translate_cmd(self, app, message: types.Message, args):
        """Перевод"""
        if not (text := args):
            if not (text := message.reply_to_message.text):
                return await utils.answer(
                    message,
                    '❌ Текст не найден'
                )
        
        if (lang := self.config.get('language')) not in LANGUAGES:
            return await utils.answer(
                message,
                f'❌ Неправильный язык (`{lang}`)'
            )
        
        translated: Translated = Translator().translate(text, dest=lang) # type: ignore
        
        await utils.answer(
            message,
            f"""
👅 Язык <b>{translated.src} -> {lang}</b>
🗣 Произношение <b>{translated.pronunciation}</b>

➡ Текст:
<b>{translated.origin}</b>

➡ Перевод:
<b>{translated.text}</b>
"""
        )

