import sys
import asyncio
from . import database, main

if sys.version_info < (3, 9, 0):
    print("Требуется Python 3.9 или выше")
    sys.exit(1)

if __name__ == "__main__":


    # import logging                          # РАЗКОММЕНТИРУЙТЕ ЭТО ЕСЛИ У ВАС БЕСКОНЕЧНАЯ ЗАГРУЗКА, И ОТПРАВЬТЕ ЛОГИ В САППОРТ ЧАТ https://t.me/UBteagram/974
    # logging.basicConfig(level=logging.INFO) # UNCOMMENT THIS IF YOU HAVE INFINITY LOADING, AND SEND LOGS TO SUPPORT CHAT https://t.me/UBteagram/974
    
    if database.db.get('teagram.loader', 'web_auth', ''):
        from .web import server
        async def serve():
            await server.serve()

        asyncio.run(serve())
    else:
        asyncio.run(main.main())
