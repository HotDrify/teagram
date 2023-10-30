from fastapi import FastAPI, Request, templating
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from telethon import TelegramClient, types, errors

from uvicorn import Config, Server
from .. import database, utils

from .tunnel import Tunnel
from .web import MainWeb

import os
import sys
import atexit
import asyncio
import logging

GREP = 'kill $(pgrep -f "ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run")'
def shutdown():
    def restart():
        os.system(GREP)
        os.execl(sys.executable, sys.executable, "-m", "teagram")

    atexit.register(restart)
    database.db.set('teagram.loader', 'web_success', True)
    database.db.pop('teagram.loader', 'web_auth')

class Web(MainWeb):
    def __init__(self, port):
        self.logger = logging.getLogger()
        self.event = asyncio.Event() 
        self.tunnel = Tunnel(self.logger, port, self.event)
        self.port = port

        super().__init__()
        
