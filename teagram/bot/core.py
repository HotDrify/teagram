import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, exceptions
from pyrogram import Client

from typing import Union, NoReturn
from loguru import logger

from .events import Events
from .token_manager import TokenManager

from .. import database, __version__, types


class BotManager(
    Events,
    TokenManager
):
    """Менеджер бота"""

    def __init__(
        self,
        app: Client,
        db: database.Database,
        all_modules: types.ModulesManager
    ) -> None:
        """Инициализация класса

        Параметры:
            app (``pyrogram.Client``):
                Клиент

            db (``database.Database``):
                База данных

            all_modules (``loader.Modules``):
                Модули
        """
        self._app = app
        self._db = db
        self._all_modules = all_modules

        self._token = self._db.get("teagram.bot", "token", None)

    async def load(self) -> Union[bool, NoReturn]:
        """Загружает менеджер бота"""
        logging.info("Загрузка менеджера бота...")
        error_text = "Юзерботу необходим бот. Реши проблему создания бота и запускай юзербот заново"

        if not self._token:
            logging.error("Токен не найден. Попытка пересоздать токен")

            token = await self._create_bot()
            self._token = token

            if self._token is False:
                logging.error(error_text)
                return sys.exit(1)

            self._db.set("teagram.bot", "token", self._token)

        try:
            self.bot = Bot(self._token, parse_mode="html")
        except (exceptions.ValidationError, exceptions.Unauthorized):
            logging.error("Неверный токен. Попытка пересоздать токен")
         
            result = await self._revoke_token()

            if not result:
                self._token = await self._create_bot()
                if not self._token:
                    logging.error(error_text)
                    return sys.exit(1)

                self._db.set("teagram.bot", "token", self._token)
                return await self.load()
            else:
                self._token = result
                self._db.set("teagram.bot", "token", self._token)

                return await self.load()

        self._dp = Dispatcher(self.bot)

        self._dp.register_message_handler(
            self._message_handler, lambda _: True,
            content_types=["any"]
        )
        self._dp.register_inline_handler(
            self._inline_handler, lambda _: True
        )
        self._dp.register_callback_query_handler(
            self._callback_handler, lambda _: True
        )

        asyncio.ensure_future(
            self._dp.start_polling())

        self.bot.manager = self

        logger.success("Менеджер бота успешно загружен")
        return True
