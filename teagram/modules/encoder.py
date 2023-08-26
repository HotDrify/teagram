from telethon.types import MessageEntityPre
from telethon.tl.custom import Message
from telethon import TelegramClient

from .. import loader, utils

@loader.module('Encoder', 'itzlayz')
class EncoderMod(loader.Module):
    async def encode_cmd(self, message: Message, args: str):
        """Добавляет entity в сообщение, c посланием"""
        client: TelegramClient = message._client # type: ignore
        if not (text := (await message.get_reply_message()).text):
            return await utils.answer(
                message,
                'Нету реплая'
            )

        await message.delete()
        await client.send_message(
            utils.get_chat(message), # type: ignore
            args,
            formatting_entities=[MessageEntityPre(0, len(args), text)]
        )

    async def decode_cmd(self, message: Message):
        """Декодирует сообщение"""
        entities = (await message.get_reply_message()).entities if await message.get_reply_message() else await utils.answer(message, 'нету реплая челлл')
        text = ' '.join([ent.language for ent in entities])
        await utils.answer(
            message,
            f'В сообщение закодировано: <code>{text}</code>'
        )