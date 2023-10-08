import sys
import asyncio
import logging

from . import main, database

if sys.version_info < (3, 9, 0):
    print("Требуется Python 3.9 или выше")
    sys.exit(1)

class TeagramStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs: list = []

    def emit(self, record):
        self.logs.append(record)

        super().emit(record)

if __name__ == "__main__":
    # РАЗКОММЕНТИРУЙТЕ ЭТО ЕСЛИ У ВАС БЕСКОНЕЧНАЯ ЗАГРУЗКА, И ОТПРАВЬТЕ ЛОГИ В САППОРТ ЧАТ https://t.me/UBteagram/974
    # UNCOMMENT THIS IF YOU HAVE INFINITY LOADING, AND SEND LOGS TO SUPPORT CHAT https://t.me/UBteagram/974
    # # logging.basicConfig(level=logging.INFO) 

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

    if database.db.get('teagram.loader', 'web_auth', ''):
        from .web import server
        async def serve():
            await server.serve()

        asyncio.run(serve())
    else:
        asyncio.run(main.main())
