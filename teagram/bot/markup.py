import typing
import functools

from .. import utils
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

def _generate_markup(self, _markup: str) -> InlineKeyboardMarkup:
    if not _markup:
        return None

    if isinstance(_markup, InlineKeyboardMarkup):
        return _markup

    _markup = InlineKeyboardMarkup()

    map_ = (
        self._units[_markup]["buttons"]
        if isinstance(_markup, str)
        else _markup
    )

    map_ = _normalize_markup(map_)

    setup_callbacks = False

    for row in map_:
        for button in row:
            if not isinstance(button, dict):
                return None

            if "callback" not in button:
                if button.get("action") == "close":
                    button["callback"] = self._close_unit_handler

                if button.get("action") == "unload":
                    button["callback"] = self._unload_unit_handler

                if button.get("action") == "answer":
                    if not button.get("message"):
                        return None

                    button["callback"] = functools.partial(
                        self._answer_unit_handler,
                        show_alert=button.get("show_alert", False),
                        text=button["message"],
                    )

            if "callback" in button and "_callback_data" not in button:
                button["_callback_data"] = utils.rand(30)
                setup_callbacks = True

            if "input" in button and "_switch_query" not in button:
                button["_switch_query"] = utils.rand(10)

    for row in map_:
        line = []
        for button in row:
            try:
                if "url" in button:
                    if not utils.check_url(button["url"]):
                        continue

                    line += [
                        InlineKeyboardButton(
                            button["text"],
                            url=button["url"],
                        )
                    ]
                elif "callback" in button:
                    line += [
                        InlineKeyboardButton(
                            button["text"],
                            callback_data=button["_callback_data"],
                        )
                    ]
                    if setup_callbacks:
                        self._custom_map[button["_callback_data"]] = {
                            "handler": button["callback"],
                            **(
                                {"always_allow": button["always_allow"]}
                                if button.get("always_allow", False)
                                else {}
                            ),
                            **(
                                {"args": button["args"]}
                                if button.get("args", False)
                                else {}
                            ),
                            **(
                                {"kwargs": button["kwargs"]}
                                if button.get("kwargs", False)
                                else {}
                            ),
                            **(
                                {"force_me": True}
                                if button.get("force_me", False)
                                else {}
                            ),
                            **(
                                {"disable_security": True}
                                if button.get("disable_security", False)
                                else {}
                            ),
                        }
                elif "input" in button:
                    line += [
                        InlineKeyboardButton(
                            button["text"],
                            switch_inline_query_current_chat=button["_switch_query"]
                            + " ",
                        )
                    ]
                elif "data" in button:
                    line += [
                        InlineKeyboardButton(
                            button["text"],
                            callback_data=button["data"],
                        )
                    ]
                elif "switch_inline_query_current_chat" in button:
                    line += [
                        InlineKeyboardButton(
                            button["text"],
                            switch_inline_query_current_chat=button[
                                "switch_inline_query_current_chat"
                            ],
                        )
                    ]
                elif "switch_inline_query" in button:
                    line += [
                        InlineKeyboardButton(
                            button["text"],
                            switch_inline_query_current_chat=button[
                                "switch_inline_query"
                            ],
                        )
                    ]
                else:
                    pass
            except KeyError:
                return False

        _markup.row(*line)

    return _markup

def _normalize_markup(
    reply_markup: str
) -> list:
    if isinstance(reply_markup, dict):
        return [[reply_markup]]

    if isinstance(reply_markup, list) and any(
        isinstance(i, dict) for i in reply_markup
    ):
        return [reply_markup]

    return reply_markup