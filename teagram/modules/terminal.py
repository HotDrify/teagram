import logging

from subprocess import check_output
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="terminal")
class terminal(loader.Module):
    """You can use bash with terminal module"""
    async def on_load(self, app: Client):
        logging.info(f"Module terminal loaded")

    async def terminal(self, app: Client, message: types.Message, args: str):
        output = check_output(args, shell=True).decode()

        await utils.answer(message, f'Args: {args}\nOutput: {output}')
