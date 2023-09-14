from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient
from .. import database

import os, sys, atexit, asyncio, configparser
from uvicorn import Config, Server


client: TelegramClient = None
login = {
    'id': 0,
    'hash': 0,
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

config = Config(api, host='127.0.0.1', port=8000)
server = Server(config)

def shutdown():
    def restart():
        os.execl(sys.executable, sys.executable, "-m", "teagram")

    atexit.register(restart)
    database.db.set('teagram.loader', 'web_success', True)
    database.db.set('teagram.loader', 'web_auth', False)

@api.post('/tokens')
async def check_tokens(data: Request):
    data = data.headers
    
    client = TelegramClient('../teagram', data['id'], data['hash'])
    await client.connect()

    login['id'] = data['id']
    login['hash'] = data['hash']
    
    config = configparser.ConfigParser()
    config["telethon"] = {
        "api_id": data['id'],
        "api_hash": data['hash']
    }

    with open("./config.ini", "w") as file:
        config.write(file)
    
    try:
        if await client.get_me():
            shutdown()
            await client.disconnect()
            asyncio.get_running_loop().stop()

            return 'Success'
        else:
            return 'Enter phone'
    except Exception as error:
        return error
    
@api.post('/phone')
async def phone_request(data: Request):
    data = data.headers

    client = TelegramClient('../teagram', login['id'], login['hash'])
    await client.connect()

    login['phone_hash'] = (await client.send_code_request(data['phone'])).phone_code_hash
    login['phone'] = data['phone']

    return 'Enter code from telegram'

@api.post('/code')
async def phonecode(data: Request):
    data = data.headers

    client = TelegramClient('../teagram', login['id'], login['hash'])
    await client.connect()

    _2fa = data.get('2fa', None)

    try:
        await client.sign_in(
            login['phone'],
            data['code'],
            phone_code_hash=login['phone_hash']
        )
    except:
        if not _2fa:
            return 'Enter 2fa password'
        
        await client.sign_in(password=_2fa)
        if not await client.get_me():
            return 'Enter valid 2fa password'
            
    shutdown()
    
    await client.disconnect()
    asyncio.get_running_loop().stop()