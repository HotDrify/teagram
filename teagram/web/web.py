from .. import database
from .tunnel import Tunnel

from fastapi import FastAPI, Request, templating, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from telethon import TelegramClient, types, errors
from uvicorn import Config, Server

import os
import sys
import atexit
import asyncio
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

class MainWeb:
    def __init__(self):
        self.api = api
        self.config = Config(api, host='0.0.0.0', port=self.port)
        self.server = Server(self.config)
        
        self.login_data = {
            'id': 123,
            'hash': "123",
            'phone': None,
            'phone_hash': None,
            'phone_code': None,
            '2fa': None
        }
        self.client = TelegramClient('./teagram',
                                     self.login_data['id'],
                                     self.login_data['hash'])
        
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
        api.add_route('/', self.index, methods=["GET"])
        api.add_route('/tokens', self.loginToClient, methods=["POST"])
        api.add_route('/qrcode', self.qrcode, methods=["GET"])
        api.add_route('/checkqr', self.checkqr, methods=["GET"])
        api.add_route('/twofa', self._2fa, methods=["GET"])

    async def index(self, request: Request):
        return templating.Jinja2Templates(
            directory='teagram/web/templates/'
        ).TemplateResponse(
            'index.html', {'request': request}
        )

    async def loginToClient(self, data: Request):
        try:
            _data = data.headers
            
            if not getattr(self.login_data, 'client', None):
                self.client = TelegramClient('./teagram', _data['id'], _data['hash'])
                await self.client.connect()

                self.login_data['self.client'] = self.client

            config = configparser.ConfigParser()
            try:
                _id = config.get('telethon', 'api_id')
                _hash = config.get('telethon', 'api_hash')
            except:
                _id = None
                _hash = None

                if not (_data['id'] and _data['hash']) and not (_id and _hash):
                    return 'Enter all api tokens'
                else:
                    config["telethon"] = {
                        "api_id": _data['id'],
                        "api_hash": _data['hash']
                    }
                    
                    with open("./config.ini", "w") as file:
                        config.write(file)

            self.login_data['id'] = _data['id'] or _id
            self.login_data['hash'] = _data['hash'] or _hash
            
            try:
                if await self.client.get_me():
                    shutdown()
                    await self.client.disconnect()
                    try:
                        asyncio.get_running_loop().stop()
                    except:
                        pass
                else:
                    await self.client.disconnect()
                    return 'qrcode'
            except Exception as error:
                await self.client.disconnect()
                return error
        except:
            await self.client.disconnect()
            await self.loginToClient(data)
    
    async def qrcode(self):
        try:
            await self.client.connect()
            qr_login = await self.client.qr_login()
            self.login_data['qr_login'] = qr_login

            return qr_login.url
        except:
            await self.client.disconnect()
            await self.qrcode()
    
    async def checkqr(self):
        try:
            await self.client.connect()
            qrlogin = await self.client.qr_login()

            if isinstance(qrlogin, types.auth.LoginTokenSuccess):
                await self.client.disconnect()
                return 'password'
            else:
                await self.client.disconnect()
        except errors.SessionPasswordNeededError:
            await self.client.disconnect()
            return 'password'

    async def _2fa(self, data: Request):
        __2fa = data.headers['2fa']
        
        await self.client.connect()
        await self.client.sign_in(password=__2fa)
        if not await self.client.get_me():
            return 'Enter valid 2fa password'
                
        shutdown()
        
        await self.client.disconnect()
        asyncio.get_running_loop().stop()