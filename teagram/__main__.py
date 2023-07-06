import sys

if sys.version_info < (3, 8, 0):
    print("Требуется Python 3.8 или выше")
    sys.exit(1)


import argparse
import asyncio

try:
    from uvloop import EventLoopPolicy
    asyncio.set_event_loop_policy(EventLoopPolicy())
    del EventLoopPolicy
except ImportError:
    pass

try:
    import ujson
    sys.modules['json'] = ujson
except ImportError:
    pass

from . import logger, main


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="teagram", description="Userbot",
        epilog="Канал: ", add_help=False
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main.main())
