import sys

from . import main

if sys.version_info < (3, 9, 0):
    print("Требуется Python 3.9 или выше")
    sys.exit(1)

import asyncio

if __name__ == "__main__":


    # import logging                          # РАЗКОММЕНТИРУЙТЕ ЭТО ЕСЛИ У ВАС БЕСКОНЕЧНАЯ ЗАГРУЗКА, И ОТПРАВЬТЕ ЛОГИ В САППОРТ ЧАТ https://t.me/UBteagram/974
    # logging.basicConfig(level=logging.INFO) # UNCOMMENT THIS IF YOU HAVE INFINITY LOADING, AND SEND LOGS TO SUPPORT CHAT https://t.me/UBteagram/974
    
    asyncio.run(main.main())
