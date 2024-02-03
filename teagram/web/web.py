#                            ██╗████████╗███████╗██╗░░░░░░█████╗░██╗░░░██╗███████╗
#                            ██║╚══██╔══╝╚════██║██║░░░░░██╔══██╗╚██╗░██╔╝╚════██║
#                            ██║░░░██║░░░░░███╔═╝██║░░░░░███████║░╚████╔╝░░░███╔═╝
#                            ██║░░░██║░░░██╔══╝░░██║░░░░░██╔══██║░░╚██╔╝░░██╔══╝░░
#                            ██║░░░██║░░░███████╗███████╗██║░░██║░░░██║░░░███████╗
#                            ╚═╝░░░╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
#                                            https://t.me/itzlayz
#                           
#                                    🔒 Licensed under the GNU AGPLv3
#                                 https://www.gnu.org/licenses/agpl-3.0.html

from .. import database

from fastapi import FastAPI, Request, templating, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from telethon import TelegramClient, types, errors
from uvicorn import Config, Server

import os
import sys
import atexit
import asyncio
import configparser

def shutdown(port):
    def restart():
        os.system(
            f'kill $(pgrep -f "ssh -o StrictHostKeyChecking=no -R 80:localhost:{port} nokey@localhost.run")'
        )
        os.execl(sys.executable, sys.executable, "-m", "teagram")

    atexit.register(restart)
    database.db.set('teagram.loader', 'web_success', True)
    database.db.pop('teagram.loader', 'web_auth')

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
api.mount(
    "/static", 
    StaticFiles(directory="teagram/web/static"), 
    "static"
)

class MainWeb:
    def __init__(self):
        self.config = Config(
            api, 
            host='0.0.0.0', 
            port=self.port,
            log_level=60
        )

        self.server = Server(self.config)
        self.login_data = {
            'id': 123,
            'hash': "___",
            'phone': None,
            'phone_hash': None,
            'phone_code': None,
            '2fa': None
        }
        self.client_error = False
        self.client = None
        
        api.add_route('/', self.index, methods=["GET"])
        api.add_route('/tokens', self.loginToClient, methods=["POST"])
        api.add_route('/qrcode', self.qrcode, methods=["GET"])
        api.add_route('/checkqr', self.checkqr, methods=["GET"])
        api.add_route('/twofa', self._2fa, methods=["POST"])

        api.add_event_handler('startup', self.proxy)

    async def proxy(self):
        asyncio.ensure_future(self.tunnel.proxytunnel())

    async def index(self, request: Request):
        return templating.Jinja2Templates(
            directory='teagram/web/templates/'
        ).TemplateResponse(
            'index.html', {'request': request}
        )

    async def loginToClient(self, data: Request):
        try:
            _data = data.headers
            _id, _hash = self._get_api_tokens(_data)

            if not self.client:
                self.client = TelegramClient('./teagram', _id, _hash)
                await self.client.connect()
            
            if not self.client.is_connected():
                await self.client.connect()

            if await self.client.get_me():
                self._shutdown()
            else:
                return Response(content='qrcode')
        except Exception as error:
            self.logger.exception(error)
            return Response(str(error))
    
    async def qrcode(self, _: Request):
        try:
            if not self.client.is_connected():
                await self.client.connect()

            qr_login = await self.client.qr_login()
            self.login_data['qr_login'] = qr_login

            return Response(qr_login.url)
        except Exception as error:
            if not self.client_error:
                await self.qrcode()
            else:
                self.client_error = False
                return Response(error)
        
    
    async def checkqr(self, _: Request):
        try:
            if not self.client.is_connected():
                await self.client.connect()

            qrlogin = await self.client.qr_login()
            password = Response(content='password')

            if isinstance(qrlogin, types.auth.LoginTokenSuccess):
                return password
            else:
                return Response()
        except errors.SessionPasswordNeededError:
            return Response(content='password')

    async def _2fa(self, data: Request):
        __2fa = data.headers['2fa']
        if not self.client.is_connected():
            await self.client.connect()

        try:
            await self.client.sign_in(password=__2fa)


            self._shutdown()
            return Response(content='')
        except errors.PasswordHashInvalidError:
            return Response(
                "Invalid 2FA password",
                status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                f"Error: {e}"
            )

    def _get_api_tokens(self, data):
        try:
            _id = int(data['id'])
        except ValueError:
            raise ValueError('Invalid api tokens')

        _hash = data['hash']
        if not _id or not _hash:
            raise ValueError('Enter all api tokens')
        
        config = configparser.ConfigParser()
        try:
            config.read('config.ini')
            config_id = config.get('telethon', 'api_id')
            config_hash = config.get('telethon', 'api_hash')

            if config_id and config_hash:
                _id, _hash = config_id, config_hash
        except (configparser.NoSectionError, configparser.NoOptionError):
            config["telethon"] = {"api_id": _id, "api_hash": _hash}
            with open("config.ini", "w") as file:
                config.write(file)

        return _id, _hash
    
    def _shutdown(self):
        shutdown(self.port)
        asyncio.get_running_loop().stop()