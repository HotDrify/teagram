import sys
import asyncio

from . import main, database

if sys.version_info < (3, 9, 0):
    print("Требуется Python 3.9 или выше")
    sys.exit(1)

if __name__ == "__main__":


    # import logging                          # РАЗКОММЕНТИРУЙТЕ ЭТО ЕСЛИ У ВАС БЕСКОНЕЧНАЯ ЗАГРУЗКА, И ОТПРАВЬТЕ ЛОГИ В САППОРТ ЧАТ https://t.me/UBteagram/974
    # logging.basicConfig(level=logging.INFO) # UNCOMMENT THIS IF YOU HAVE INFINITY LOADING, AND SEND LOGS TO SUPPORT CHAT https://t.me/UBteagram/974
    
    import logging
    from logging import StreamHandler
    class CustomStreamHandler(StreamHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logs: list = []

        def emit(self, record):
            self.logs.append(record)

            super().emit(record)

    handler = CustomStreamHandler()
    fmt = logging.Formatter(
        '[%(asctime)s] %(name)s:%(levelname)s > %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )

    handler.setFormatter(fmt)
    log = logging.getLogger()
    log.addHandler(handler)

    if database.db.get('teagram.loader', 'web_auth', ''):
        from .web import server
        async def serve():
            await server.serve()

        asyncio.run(serve())
    else:
        asyncio.run(main.main())
