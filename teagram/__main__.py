import sys

if sys.version_info < (3, 8, 0):
    print("Требуется Python 3.8 или выше\nNeeds Python 3.8 or above")
    sys.exit(1)


import argparse
import asyncio

from . import logger, main


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="teagram"
    )

    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main.main())