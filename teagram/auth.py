import logging

import sys
import configparser

from . import database
from datetime import datetime
from getpass import getpass

from typing import Union, Tuple, NoReturn

from pyrogram import Client, types, errors
from pyrogram.session.session import Session

from . import __version__

Session.notice_displayed = True
data = database.load_db()

class Auth:
    """Авторизация в аккаунт"""

    def __init__(self, session_name: str = "../teagram") -> None:
        self._check_api_tokens()
        self.app = Client(
            name=session_name, api_id=data.get('api_id'), api_hash=data.get('api_hash'),
            parse_mode="html", app_version=f"teagram v{__version__}"
        )

    def _check_api_tokens(self) -> bool:
        """Проверит установлены ли токены, если нет, то начинает установку"""
        config = configparser.ConfigParser()
        if not config.read("./config.ini"):
            config["pyrogram"] = {
                "api_id": data.get('api_id'),
                "api_hash": data.get('api_hash')
            }

            with open("./config.ini", "w") as file:
                config.write(file)

        return True

    async def send_code(self) -> Tuple[str, str]:
        """Отправить код подтверждения"""
        while True:
            error_text: str = None

            try:
                phone = input("Введи номер телефона: ")
                return phone, (await self.app.send_code(phone)).phone_code_hash
            except errors.PhoneNumberInvalid:
                error_text = "Неверный номер телефона, попробуй ещё раз"
            except errors.PhoneNumberBanned:
                error_text = "Номер телефона заблокирован"
            except errors.PhoneNumberFlood:
                error_text = "На номере телефона флудвейт"
            except errors.PhoneNumberUnoccupied:
                error_text = "Номер не зарегистрирован"
            except errors.BadRequest as error:
                error_text = f"Произошла неизвестная ошибка: {error}"

            if error_text:
                logging.error(error_text)

    async def enter_code(self, phone: str, phone_code_hash: str) -> Union[types.User, bool]:
        """Ввести код подтверждения"""
        try:
            code = input("Введи код подтверждения: ")
            return await self.app.sign_in(phone, phone_code_hash, code)
        except errors.SessionPasswordNeeded:
            return False

    async def enter_2fa(self) -> types.User:
        """Ввести код двухфакторной аутентификации"""
        while True:
            try:
                passwd = getpass("Введи пароль двухфакторной аутентификации: ")
                return await self.app.check_password(passwd)
            except errors.BadRequest:
                logging.error("Неверный пароль, попробуй снова")

    async def authorize(self) -> Union[Tuple[types.User, Client], NoReturn]:
        """Процесс авторизации в аккаунт"""
        await self.app.connect()

        try:
            me = await self.app.get_me()
        except errors.AuthKeyUnregistered:
            phone, phone_code_hash = await self.send_code()
            logged = await self.enter_code(phone, phone_code_hash)
            if not logged:
                me = await self.enter_2fa()
        except errors.SessionRevoked:
            logging.error("Сессия была сброшена, введи rm teagram.session и заново введи команду запуска")
            await self.app.disconnect()
            return sys.exit(64)

        return me, self.app
