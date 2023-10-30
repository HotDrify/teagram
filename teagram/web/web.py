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
import contextlib
import configparser

GREP = 'kill $(pgrep -f "ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run")'

def shutdown():
    def restart():
        os.system(GREP)
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
        self.config = Config(api, host='0.0.0.0', port=self.port)
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
        self.client = TelegramClient('./teagram',
                                     self.login_data['id'],
                                     self.login_data['hash'])
        
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

            if self.client.api_hash != 123:
                self.client = TelegramClient('./teagram', _id, _hash)
                await self.client.connect()
            
            if not self.client.is_connected():
                await self.client.connect()

            if await self.client.get_me():
                self._shutdown()
            else:
                await self.client.disconnect()
                return Response('qrcode')
        except Exception as error:
            await self.client.disconnect()
            return Response(str(error))
    
    async def qrcode(self, _: Request):
        try:
            await self.client.connect()
            qr_login = await self.client.qr_login()
            self.login_data['qr_login'] = qr_login

            return Response(qr_login.url)
        except Exception as error:
            if not self.client_error:
                await self.qrcode()
            else:
                self.client_error = False
                print(error)
                return Response(error)
        
    
    async def checkqr(self, _: Request):
        try:
            await self.client.connect()
            qrlogin = await self.client.qr_login()

            if isinstance(qrlogin, types.auth.LoginTokenSuccess):
                return Response('password')
            else:
                return Response("password")
        except errors.SessionPasswordNeededError:
            return Response('password')
        finally:
            await self.client.disconnect()

    async def _2fa(self, data: Request):
        __2fa = data.headers['2fa']
        
        await self.client.connect()
        await self.client.sign_in(password=__2fa)
        if not await self.client.get_me():
            return Response('Enter valid 2FA password')
        
        await self.client.disconnect()
        self._shutdown()

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
        shutdown()
        with contextlib.suppress(Exception):
            asyncio.get_running_loop().stop()