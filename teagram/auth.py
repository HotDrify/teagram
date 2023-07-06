import logging

import sys
import configparser

from . import db
from datetime import datetime
from getpass import getpass

from typing import Union, Tuple, NoReturn

from pyrogram import Client, types, errors
from pyrogram.session.session import Session

from . import __version__

Session.notice_displayed = True
data = db.load_db()

api_id = str(data.get('api_id'))
api_hash = data.get('api_hash')


class Auth:
    """Авторизация в аккаунт"""

    def __init__(self, session_name: str = "../teagram") -> None:
        self._check_api_tokens()
        self.app = Client(
            name=session_name, api_id=api_id, api_hash=api_hash,
            parse_mode="html", app_version=f"teagram v{__version__}"
        )

    def _check_api_tokens(self) -> bool:
        """Проверит установлены ли токены, если нет, то начинает установку"""
        config = configparser.ConfigParser()
        if not config.read("./config.ini"):
            config["pyrogram"] = {
                "api_id": api_id,
                "api_hash": api_hash
            }

            with open("./config.ini", "w") as file:
                config.write(file)

        return True

    async def send_code(self) -> Tuple[str, str]:
        """Отправить код подтверждения"""
        while True:
            error_text: str = None

            try:
                phone = input(
                    "Введи номер телефона\nEnter phone number: ")
                return phone, (await self.app.send_code(phone)).phone_code_hash
            except errors.PhoneNumberInvalid:
                error_text = "Неверный номер телефона, попробуй ещё раз\nWrong phone number, try again"
            except errors.PhoneNumberBanned:
                error_text = "Номер телефона заблокирован\nPhone number banned"
            except errors.PhoneNumberFlood as e:
                seconds = e.seconds
                error_text = f"Слишком много попыток входа, пожалуйста подождите {e.seconds}\n\
                    Too many login attempts, please wait {e.seconds}"
            except errors.PhoneNumberUnoccupied:
                error_text = "Номер не зарегистрирован\nNumber not registered"
            except errors.BadRequest as error:
                error_text = f"Произошла неизвестная ошибка: {error}\nAn unknown error occurred: {error}"

            if error_text:
                logging.error(error_text)

    async def enter_code(self, phone: str, phone_code_hash: str) -> Union[types.User, bool]:
        """Ввести код подтверждения"""
        try:
            code = input(
                "Введи код подтверждения\nEnter confirmation code: ")
            return await self.app.sign_in(phone, phone_code_hash, code)
        except errors.SessionPasswordNeeded:
            return False

    async def enter_2fa(self) -> types.User:
        """Ввести код двухфакторной аутентификации"""
        while True:
            try:
                passwd = getpass(
                    "Введи пароль двухфакторной аутентификации (2FA PASS): ")
                return await self.app.check_password(passwd)
            except errors.BadRequest:
                logging.error(
                    "Неверный пароль, попробуй снова\nWrong password, try again")

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
            logging.error(
                "Сессия была сброшена, удали teagram.session и заново введи команду запуска\n\
                    Session was revoked, remove teagram.session and restart")
            await self.app.disconnect()
            return sys.exit(64)

        return me, self.app
