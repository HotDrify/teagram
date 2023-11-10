import os
import sys
import asyncio
import logging

from . import main, database
from .utils import get_platform
from .web import Web

if sys.version_info < (3, 9, 0):
    print("Needs python 3.9 or higher")
    sys.exit(1)

if __name__ == "__main__":
    if database.db.get('teagram.loader', 'web_auth', ''):
        import socket
        from random import randint
        from contextlib import closing

        port = randint(1000, 65535)
        if 'windows' not in get_platform().lower():
            while True:
                port = randint(1000, 65535)
                try:
                    with socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM
                        ) as sock:
                        sock.bind(("localhost", port))

                    break
                except OSError as e:
                    if e.errno == 98:
                        continue

        web_config = Web(port)
        async def serve():
            await web_config.server.serve()

        try:
            asyncio.run(serve())
        except:
            pass
    else:
        try:
            asyncio.run(main.main())
        except:
            logging.getLogger().info("Goodbye!")
