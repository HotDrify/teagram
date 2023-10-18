import os
import sys
import asyncio
import logging

from . import main, database
from .web import server

if sys.version_info < (3, 9, 0):
    print("Needs python 3.9 or higher")
    sys.exit(1)

class TeagramStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = {
            'INFO': [],
            'WARNING': [],
            'ERROR': [],
            'CRITICAL': [],
            'DEBUG': [],
            'NOTSET': []
        }

        with open("teagram.log", "w", encoding='utf-8') as l:
            l.write("")

    def emit(self, record):
        lvl = logging.getLevelName(record.levelno)
        self.logs[lvl].append(record)

        with open("teagram.log", "a", encoding='utf-8') as l:
            l.write(f'{self.format(record)}\n')
        
        super().emit(record)

if __name__ == "__main__":
    fmt = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    handler = TeagramStreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(fmt)

    log = logging.getLogger()
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    logging.getLogger('telethon').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    
    try:
        if os.geteuid() == 0:
            log.warning("Please do not use root for userbot!!!")
    except:
        pass

    if database.db.get('teagram.loader', 'web_auth', ''):
        async def serve():
            await server.serve()

        asyncio.run(serve())
    else:
        try:
            asyncio.run(main.main())
        except:
            logging.getLogger().info("Goodbye!")
