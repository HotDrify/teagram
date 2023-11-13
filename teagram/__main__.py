import sys
import asyncio
import argparse

from .main import Main

if sys.version_info < (3, 9, 0):
    print("Needs python 3.9 or higher")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--disable-web",
    action="store_true",
    help="Disable auth with web"
)

if __name__ == "__main__":
    asyncio.run(
        Main(
            parser.parse_args()
        ).main()
    )
