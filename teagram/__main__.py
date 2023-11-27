import sys
import asyncio
import argparse

if sys.version_info < (3, 9, 0):
    print("Needs python 3.9 or higher")
    sys.exit(1)

from .main import Main
from contextlib import suppress

parser = argparse.ArgumentParser()
parser.add_argument(
    "--disable-web",
    action="store_true",
    help="Disable auth with web"
)

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        args = parser.parse_args()
        main = Main(args).main
        asyncio.run(main())