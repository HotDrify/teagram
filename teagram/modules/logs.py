import logging

from pyrogram import Client, types

from .. import database, loader, utils

@loader.module(name="Logging")
class loggingMod(loader.Module):
    """Simple logging with teagram"""
    
    # logging messages
    @loader.on(lambda _, __, message: not message.from_user.is_self)
    async def watcher_messages(self, app: Client, message: types.Message):
        return await app.send_message(
            'me',
            '[INFO] 🍵 - message from {}: {}'.format(
                message.from_user.first_name,
                message.text or message.media
            )
        )

    # logging commands
    @loader.on(lambda _, __, message: not message.media and message.text.startswith('.'))
    async def watcher_commands(self, app: Client, message: types.Message):
        return await app.send_message(
            'me',
            '[INFO] 🍵 - command from {}: {}'.format(
                message.from_user.first_name,
                message.text.split()[0]
            )
        )
