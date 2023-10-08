from fastapi import FastAPI, Request, templating
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient, types, errors
from .. import database, utils

import os, re, sys, atexit, asyncio, configparser
from uvicorn import Config, Server

GREP = 'kill $(pgrep -f "ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run")'

client: TelegramClient = None
login = {
    'id': 123,
    'hash': "123_",
    'phone': 0,
    'phone_hash': 0,
    'phone_code': 0,
    '2fa': 0
}

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
api.mount("/static", StaticFiles(directory="teagram/web/static"), name="static")

config = Config(api, host='127.0.0.1', port=8000, log_level=60)
server = Server(config)

def shutdown():
    def restart():
        os.system(GREP)
        os.execl(sys.executable, sys.executable, "-m", "teagram")

    atexit.register(restart)
    database.db.set('teagram.loader', 'web_success', True)
    database.db.pop('teagram.loader', 'web_auth')

@api.on_event('startup')
async def proxytunnel():
    print('Getting url...')

    url = None
    if 'windows' not in utils.get_platform().lower():
        stream = await asyncio.create_subprocess_shell(
            'ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        ev = asyncio.Event()
        url = ''

        async def gettext():
            for line in iter(stream.stdout.readline, ""):
                line = (await line).decode()
                if (ur := re.search(r"tunneled.*?(https:\/\/.+)", line)):
                    nonlocal url
                    url = ur[1]
                    if not ev.is_set():
                        ev.set()

        asyncio.ensure_future(gettext())
        await asyncio.wait_for(ev.wait(), 15)

    if url:
        atexit.register(lambda: os.system(GREP))
        print(f'To login in account, open in browser {url}')
    else:
        print('To login in account, open in browser https://127.0.0.1:8000')

@api.get('/')
async def home(request: Request):
    return templating.Jinja2Templates(
        directory='teagram/web/'
    ).TemplateResponse(
        'index.html', {'request': request}
    )

@api.post('/tokens')
async def check_tokens(data: Request):
    try:
        _data = data.headers
        
        if not getattr(login, 'client', None):
            client = TelegramClient('./teagram', _data['id'], _data['hash'])
            await client.connect()

            login['client'] = client

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

        login['id'] = _data['id'] or _id
        login['hash'] = _data['hash'] or _hash
        
        try:
            if await client.get_me():
                shutdown()
                await client.disconnect()
                try:
                    asyncio.get_running_loop().stop()
                except:
                    pass
            else:
                await client.disconnect()
                return 'choice'
        except Exception as error:
            await client.disconnect()
            return error
    except:
        await client.disconnect()
        await check_tokens(data)
    
@api.get('/qrcode')
async def qrcode():
    try:
        if not getattr(login, 'client', None):
            client = TelegramClient('./teagram', login['id'], login['hash'])
            await client.connect()

            login['client'] = client

        qr_login = await client.qr_login()
        login['qr_login'] = qr_login

        return qr_login.url
    except:
        await client.disconnect()
        await qrcode()
    
@api.get('/checkqr')
async def checkqr():
    try:
        if not getattr(login, 'client', None):
            client = TelegramClient('./teagram', login['id'], login['hash'])
            await client.connect()

            login['client'] = client

        qrlogin = await client.qr_login()

        if isinstance(qrlogin, types.auth.LoginTokenSuccess):
            await client.disconnect()
            return 'password'
        else:
            await client.disconnect()
    except errors.SessionPasswordNeededError:
        await client.disconnect()
        return 'password'

@api.post('/twofa')
async def _2fa(data: Request):
    data = data.headers

    if not getattr(login, 'client', None):
        client = TelegramClient('./teagram', login['id'], login['hash'])
        await client.connect()

        login['client'] = client

    __2fa = data.get('2fa', '____________')
    await client.sign_in(password=__2fa)
    if not await client.get_me():
        return 'Enter valid 2fa password'
            
    shutdown()
    
    await client.disconnect()
    asyncio.get_running_loop().stop()