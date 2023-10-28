from fastapi import FastAPI, Request, templating
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient, types, errors
from .. import database, utils

import os, re, sys, atexit, asyncio, configparser, logging
from uvicorn import Config, Server

GREP = 'kill $(pgrep -f "ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run")'
def shutdown():
    def restart():
        os.system(GREP)
        os.execl(sys.executable, sys.executable, "-m", "teagram")

    atexit.register(restart)
    database.db.set('teagram.loader', 'web_success', True)
    database.db.pop('teagram.loader', 'web_auth')

class Tunnel:
    def __init__(self, logger: logging.Logger, port: int, event: asyncio.Event):
        self.logger = logger
        self.stream = None
        self.port = port
        self.ev = event

    def terminate(self):
        try:
            self.stream.terminate()
        except:
            self.logger.exception("Can't terminate stream")
            return False

        self.logger.info('Stream terminated')
        return True

    async def proxytunnel(self):
        self.logger.info("Processing...")

        url = None
        if 'windows' not in utils.get_platform().lower():
            self.stream = await asyncio.create_subprocess_shell(
                "ssh -o StrictHostKeyChecking=no -R "
                f"80:localhost:{self.port} nokey@localhost.run",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            url = ''

            async def gettext():
                for line in iter(self.stream.stdout.readline, ""):
                    line = (await line).decode()
                    await asyncio.sleep(1)

                    if (ur := re.search(r"tunneled.*?(https:\/\/.+)", line)):
                        nonlocal url
                        url = ur[1]
                        
                        if not self.ev.is_set():
                            self.ev.set()

            asyncio.ensure_future(gettext())
            try:
                await asyncio.wait_for(self.ev.wait(), 10)
            except:
                self.terminate()
        else:
            self.logger.info("Proxy isn't working on windows, please use WSL")

        if url:
            atexit.register(lambda: os.system(GREP))
            self.logger.info(f'To login in account, open in browser {url}')
        else:
            self.logger.info(f'To login in account, open in browser http://localhost:{self.port}')

class Web:
    def __init__(self, port):
        self.logger = logging.getLogger()
        self.event = asyncio.Event() 
        self.tunnel = Tunnel(self.logger, port, self.event)
        self.port = port

        self.api = FastAPI()
        self.config = Config(self.api, host='0.0.0.0', port=self.port)
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
        
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        )
        self.api.mount(
            "/static", 
            StaticFiles(directory="teagram/web/static"), 
            name="static"
        )

        @self.api.on_event('startup')
        async def proxy():
            asyncio.ensure_future(self.tunnel.proxytunnel())

        @self.api.get('/')
        async def home(request: Request):
            return templating.Jinja2Templates(
                directory='teagram/web/'
            ).TemplateResponse(
                'index.html', {'request': request}
            )

        @self.api.post('/tokens')
        async def check_tokens(data: Request):
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
                await check_tokens(data)
            
        @self.api.get('/qrcode')
        async def qrcode():
            try:
                await self.client.connect()
                qr_login = await self.client.qr_login()
                self.login_data['qr_login'] = qr_login

                return qr_login.url
            except:
                await self.client.disconnect()
                await qrcode()
            
        @self.api.get('/checkqr')
        async def checkqr():
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

        @self.api.post('/twofa')
        async def _2fa(data: Request):
            data = data.headers

            __2fa = data.get('2fa', '____________')
            
            await self.client.connect()
            await self.client.sign_in(password=__2fa)
            if not await self.client.get_me():
                return 'Enter valid 2fa password'
                    
            shutdown()
            
            await self.client.disconnect()
            asyncio.get_running_loop().stop()

        