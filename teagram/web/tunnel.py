from ..utils import get_platform

import os
import re
import atexit
import asyncio
import logging


GREP = 'kill $(pgrep -f "ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run")'

class Tunnel:
    def __init__(self, logger: logging.Logger, port: int, event: asyncio.Event):
        self.logger = logger
        self.stream = None
        self.port = port
        self.ev = event

    def terminate(self):
        try:
            self.stream.terminate()
        except Exception as error:
            self.logger.error(f"Can't terminate stream ({error})")
            return False

        self.logger.debug("Can't make tunnel, stream terminated")
        return True

    async def proxytunnel(self):
        self.logger.info("Processing...")

        url = None
        if 'windows' not in get_platform().lower():
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
                await asyncio.wait_for(self.ev.wait(), 30)
            except Exception:
                self.terminate()
        else:
            self.logger.info("Proxy isn't working on windows, please use WSL")

        if url:
            atexit.register(lambda: os.system(GREP))
            self.logger.info(f'To login in account, open in browser {url}')
        else:
            self.logger.info(f'To login in account, open in browser http://localhost:{self.port}')