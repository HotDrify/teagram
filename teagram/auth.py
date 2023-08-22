import configparser
import logging
import sys

import base64
import asyncio

from datetime import datetime
from getpass import getpass
from typing import NoReturn, Tuple, Union

from telethon.password import compute_check
from telethon import TelegramClient, errors, types
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.auth import CheckPasswordRequest

from qrcode.main import QRCode


from . import __version__

# Session.notice_displayed: bool = True


class Auth:
    """Авторизация в аккаунт"""

    def __init__(self, session_name: str = "../teagram") -> None:
        self._check_api_tokens()

        config = configparser.ConfigParser()
        config.read("./config.ini")

        self.app: TelegramClient = TelegramClient(
            session=session_name, api_id=int(config.get('telethon', 'api_id')),
            api_hash=config.get('telethon', 'api_hash'), app_version=f"v{__version__}"
        )

    def _check_api_tokens(self) -> bool:
        config = configparser.ConfigParser()
        if not config.read("./config.ini"):
            config["telethon"] = {
                "api_id": input("Введи API ID: "),
                "api_hash": input("Введи API hash: ")
            }

            with open("./config.ini", "w") as file:
                config.write(file)
        
        return True

    async def send_code(self) -> Tuple[str, str]:
        """Enter phone number"""
        while True:
            error_text: str = ""

            try:
                phone = input("Enter phone number: ")
                return phone, (await self.app.send_code_request(phone)).phone_code_hash
            except errors.PhoneNumberInvalidError:
                error_text = "Неверный номер телефона, попробуй ещё раз"
            except errors.PhoneNumberBannedError:
                error_text = "Номер телефона заблокирован"
            except errors.PhoneNumberFloodError:
                error_text = "На номере телефона флудвейт"
            except errors.PhoneNumberUnoccupiedError:
                error_text = "Номер не зарегистрирован"
            except errors.BadRequestError as error:
                error_text = f"Произошла неизвестная ошибка: {error}"

            if error_text:
                logging.error(error_text)

    async def enter_code(self, phone: str, phone_code_hash: str) -> Union[types.User, bool]:
        """Login in account"""
        try:
            code = input("Enter confirmation code: ")
            passwd = getpass("Enter 2FA passowrd: ")

            return await self.app.sign_in(
                phone,
                code,
                password=passwd,
                phone_code_hash=phone_code_hash
            ) # type: ignore
        except errors.SessionPasswordNeededError:
            return False
        except errors.PasswordHashInvalidError:
            logging.error("Wrong password")

    async def authorize(self) -> Union[Tuple[types.User, TelegramClient], NoReturn]:
        """Account authorization process"""
        await self.app.connect()

        try:
            me = await self.app.get_me()
            if not me:
                raise errors.AuthKeyUnregisteredError('asd')
        except errors.AuthKeyUnregisteredError:
            qr = input("Login by QR-CODE? y/n ").lower().split()

            if qr[0] == "y":
                tries = 0
                while True:                    
                    try:
                        qrcode = await self.app.qr_login()
                    except errors.UnauthorizedError:                        
                        break

                    if isinstance(qrcode, types.auth.LoginTokenSuccess):
                        break
                    if tries % 30 == 0:
                        print('Settings > Devices > Scan QR Code (or Add device)\n')
                        print('Scan QR code below:' )

                        await qrcode.recreate()
                        qr = QRCode()
                        qr.clear()
                        qr.add_data(qrcode.url)
                        qr.print_ascii()
                    
                    tries += 1
                    await asyncio.sleep(1)
                
                password = await self.app(GetPasswordRequest())

                while True:
                    twofa = getpass('Enter 2FA password: ')
                    try:
                        await self.app._on_login(
                            await self.app(CheckPasswordRequest(compute_check(password, twofa.strip())).user)
                        )
                    except errors.PasswordHashInvalidError:
                        logging.error('Wrong password!')
                    else:
                        break

                me = await self.app.get_me()
                    
            else:
                phone, phone_code_hash = await self.send_code() # type: ignore
                await self.enter_code(phone, phone_code_hash)
                
                me: types.User = await self.app.get_me()
        except errors.SessionRevokedError:
            logging.error("The session was revoked, delete the session and re-enter the start command")
            self.app.disconnect()

            return sys.exit(64)

        return me, self.app