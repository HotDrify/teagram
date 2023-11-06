import typing
import logging
from aiogram import types

logger = logging.getLogger()

class Utils:
    def __init__(self) -> None:
        self.markup_keywords = [
            "text", 
            "callback", 
            "url",
            "input",
            "login_url"
        ]

    def _generate_markup(
            self, 
            markup: typing.List[typing.Dict]
            ) -> typing.Union[types.InlineKeyboardMarkup, None]:
        """
        Generates markup from list
        :param markup: list with dicts
        :return: `types.InlineKeyboardMarkup` or `None`
        """
        if not markup:
            return None

        keyboard = types.InlineKeyboardMarkup()
        for btn in markup:
            try:
                if btn.get('callback', ''):
                    if isinstance(btn['callback'], str):
                        keyboard.add(
                            types.InlineKeyboardButton(
                                btn['text'],
                                callback_data=btn['callback']
                            )
                        )
                    else:
                        logger.debug("Button's callback must be string")
                elif btn.get('input', ''):
                    keyboard.add(
                        types.InlineKeyboardButton(
                            btn['text'],
                            switch_inline_query_current_chat=btn['input']
                        )
                    )
                elif btn.get('url', ''):
                    keyboard.add(
                        types.InlineKeyboardButton(
                            btn['text'],
                            url=btn['url']
                        )
                    )
                elif btn.get('login_url', ''):
                    keyboard.add(
                        types.InlineKeyboardButton(
                            btn['text'],
                            login_url=btn['login_url']
                        )
                    )
            except KeyError as e:
                logger.debug(f"Can't build button: {e}")

        return keyboard