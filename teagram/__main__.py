from sys import version_info

if version_info < (3, 8, 0):
    print("Требуется Python 3.8 или выше\nNeeds Python 3.8 or above")
    exit(1)


from argparse import ArgumentParser
import asyncio

try:
    from uvloop import EventLoopPolicy
    asyncio.set_event_loop_policy(EventLoopPolicy())
    del EventLoopPolicy
except ImportError:
    pass

from . import main


def parse_arguments():
    parser = ArgumentParser(
        prog="teagram"
    )

    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main.main())
