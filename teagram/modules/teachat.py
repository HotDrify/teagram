from .. import loader, utils

from telethon.types import ChatAdminRights
from telethon.custom import Message
from telethon.errors import ChatAdminRequiredError, UserIdInvalidError, UserNotParticipantError

@loader.module('Teachat', 'itzlayz', 1.0)
class TeachatMod(loader.Module):
    def __init__(self):
        self.admin = ChatAdminRights(
            True, True, True, True, True, True, True, True, False, True, True, True
        )
        self.NonAdmin = ChatAdminRights(
            False, False, False, False, False, False, False, False, False, False, False, False
        )

    @loader.command()
    async def mutecmd(self, message: Message, args):
        if not args:
            if not (reply := await message.get_reply_message()):
                return await utils.answer(
                    message,
                    f'❌ Вы не указали юзера или реплай'
                )

        try:
            chat = utils.get_chat(message)
            user_id = int((args or reply.sender_id))
            await self.client.edit_permissions(chat, user_id, send_messages=False)
            await utils.answer(message, "✔ Пользователь замучен.")
        except (ValueError, ChatAdminRequiredError, UserIdInvalidError, UserNotParticipantError) as e:
            await utils.answer(message, f"❌ Произошла ошибка: {e}")

    @loader.command()
    async def unmute(self, message: Message, args):
        if not args:
            if not (reply := await message.get_reply_message()):
                return await utils.answer(
                    message,
                    f'❌ Вы не указали юзера или реплай'
                )

        try:
            chat = utils.get_chat(message)
            user_id = int((args or reply.sender_id))
            await self.client.edit_permissions(chat, user_id, send_messages=True)
            await utils.answer(message, "✔ Пользователь размучен.")
        except (ValueError, ChatAdminRequiredError, UserIdInvalidError, UserNotParticipantError) as e:
            await utils.answer(message, f"❌ Произошла ошибка: {e}")

    @loader.command()
    async def pincmd(self, message: Message, args):
        try:
            if not (reply := await message.get_reply_message()):
                return await utils.answer(
                    message,
                    f'❌ Вы не указали реплай'
                )

            await reply.pin(notify=bool(args))
            await utils.answer(message, "✔ Сообщение закреплено.")
        except Exception as e:
            await utils.answer(message, f"❌ Произошла ошибка: {e}")

    @loader.command()
    async def unpin(self, message: Message, args):
        try:
            if not (reply := await message.get_reply_message()):
                return await utils.answer(
                    message,
                    f'❌ Вы не указали реплай'
                )

            await reply.unpin(notify=bool(args))
            await utils.answer(message, "✔ Сообщение откреплено.")
        except Exception as e:
            await utils.answer(message, f"❌ Произошла ошибка: {e}")