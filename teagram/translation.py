import os
import typing

from . import utils
from .database import Database

LANGUAGES = list(
    map(
        lambda x: x.replace('.yml', ''),
        os.listdir('teagram/langpacks')
    )
)

class Translator:
    def __init__(self, db: Database):
        self.db = db
        self.lang = None
        self.translations = {}
    
    def load_translation(self):
        self.lang = self.db.get('teagram.loader', 'lang', None)
        self.translations = utils.get_langpack()

class Strings:
    def __init__(self, module, translator: Translator):
        self.module = module
        self.translator = translator

        translator.load_translation()
        self.name = module.__class__.__name__.replace("Mod", "").lower()
        self.strings = translator.translations.get(self.name)
        self._strings = getattr(module, 'strings', {})
    
    def get(self, key: str) -> str:
        try:
            return self.translator.translations[self.name][key]
        except KeyError:
            try:
                return self.translator.translations[self.module.name.lower()][key]
            except KeyError:
                for lang in LANGUAGES:
                    if lang == self.translator.lang:
                        if (
                            hasattr(self.module, f'strings_{lang}')
                            and key in getattr(self.module, f'strings_{lang}')
                        ):
                            return getattr(self.module, f'strings_{lang}').get(key)
                        else:
                            return self._strings.get(key, None)

    def __getitem__(self, key: str) -> str:
        return self.get(key)

    def __call__(
        self, 
        key: str, 
        _: typing.Optional[typing.Any] = None
    ) -> str: 
        return self.get(key)