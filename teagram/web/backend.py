from .tunnel import Tunnel
from .web import MainWeb

import asyncio
import logging

class Web(MainWeb):
    def __init__(self, port):
        self.logger = logging.getLogger()
        self.event = asyncio.Event() 
        self.tunnel = Tunnel(self.logger, port, self.event)
        self.port = port

        super().__init__()
        
