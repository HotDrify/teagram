import configparser
import logging
import sys

import base64
import asyncio

from datetime import datetime
from getpass import getpass
from typing import NoReturn, Tuple, Union

from pyrogram import Client, errors, types, raw
from pyrogram.session.session import Session
from pyrogram.raw.functions.auth.export_login_token import ExportLoginToken

from qrcode.main import QRCode


from . import __version__

Session.notice_displayed: bool = True


def colored_input(prompt: str = "", hide: bool = False) -> str:
    """Цветной инпут"""
    frame = sys._getframe(1)
    return (input if not hide else getpass)(
        "\x1b[32m{time:%Y-%m-%d %H:%M:%S}\x1b[0m | "
        "\x1b[1m{level: <8}\x1b[0m | "
        "\x1b[36m{name}\x1b[0m:\x1b[36m{function}\x1b[0m:\x1b[36m{line}\x1b[0m - \x1b[1m{prompt}\x1b[0m".format(
            time=datetime.now(), level="INPUT", name=frame.f_globals["__name__"],
            function=frame.f_code.co_name, line=frame.f_lineno, prompt=prompt
        )
    )


class Auth:
    """Авторизация в аккаунт"""

    def __init__(self, session_name: str = "../teagram") -> None:
        self._check_api_tokens()

        config = configparser.ConfigParser()
        config.read("./config.ini")

        self.app = Client(
            name=session_name, api_id=config.get('pyrogram', 'api_id'),
            api_hash=config.get('pyrogram', 'api_hash'),
            app_version=f"v{__version__}"
        )

    def _check_api_tokens(self) -> bool:
        """Проверит установлены ли токены, если нет, то начинает установку"""
        config = configparser.ConfigParser()
        if not config.read("./config.ini"):
            config["pyrogram"] = {
                "api_id": colored_input("Введи API ID: "),
                "api_hash": colored_input("Введи API hash: ")
            }

            with open("./config.ini", "w") as file:
                config.write(file)
        
        return True

    async def send_code(self) -> Tuple[str, str]:
        """Отправить код подтверждения"""
        while True:
            error_text: str = ""

            try:
                phone = colored_input("Введи номер телефона: ")
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
            code = colored_input("Введи код подтверждения: ")
            
            return await self.app.sign_in(phone, phone_code_hash, code)
        except errors.SessionPasswordNeeded:
            return False

    async def enter_2fa(self) -> types.User:
        """Ввести код двухфакторной аутентификации"""
        while True:
            try:
                passwd = colored_input("Введи пароль двухфакторной аутентификации: ", True)

                return await self.app.check_password(passwd)
            except errors.BadRequest:
                logging.error("Неверный пароль, попробуй снова")

    async def authorize(self) -> Union[Tuple[types.User, Client], NoReturn]:
        """Процесс авторизации в аккаунт"""
        await self.app.connect()

        try:
            me = await self.app.get_me()
        except errors.AuthKeyUnregistered:
            config = configparser.ConfigParser()
            config.read('config.ini')

            qr = colored_input("Вход по QR-CODE? y/n ").lower().split()

            if qr[0] == "y":
                api_id = int(config.get("pyrogram","api_id"))
                api_hash = config.get("pyrogram","api_hash")

                tries = 0
                while True:                    
                    try:
                        r = await self.app.invoke(
                            ExportLoginToken(
                                api_id=api_id, api_hash=api_hash, except_ids=[]
                            )
                        )
                    except errors.exceptions.unauthorized_401.SessionPasswordNeeded:
                        me: types.User = await self.enter_2fa()
                        
                        break

                    if isinstance(r, raw.types.auth.login_token_success.LoginTokenSuccess):
                        break
                    if isinstance(r, raw.types.auth.login_token.LoginToken) and tries % 30 == 0:
                        print('Settings > Devices > Scan QR Code (or Add device)\n'
                          'Настройки > Устройства > Подключить устройство')
                        print('Scan QR code below | Сканируйте QR код ниже:' )

                        qr = QRCode(error_correction=1)

                        qr.add_data('tg://login?token={}'.format(
                            base64.urlsafe_b64encode(r.token).decode('utf-8').rstrip('=') # type: ignore
                        ))

                        qr.make(fit=True)
                        qr.print_ascii()
                    
                    tries += 1
                    await asyncio.sleep(1)
                    
            else:
                phone, phone_code_hash = await self.send_code() # type: ignore
                logged = await self.enter_code(phone, phone_code_hash)
                if not logged:
                    me: types.User = await self.enter_2fa()
                else:
                    me: types.User = await self.app.get_me()
        except errors.SessionRevoked:
            logging.error("Сессия была сброшена, удали сессию и заново введи команду запуска")
            await self.app.disconnect()
            return sys.exit(64)

        return me, self.app