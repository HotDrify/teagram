import logging
import asyncio
import time
import sys
import re
from typing import Union

from telethon import errors
from telethon.tl.functions.contacts import UnblockRequest

from .. import utils
from .types import Item

logger = logging.getLogger()

class TokenManager(Item):
    """
    Token manager class.
    Manages the creation and revocation of bot tokens.
    """

    async def _create_bot(self) -> Union[str, None]:
        """
        Create and configure a bot.
        
        Returns:
            Union[str, None]: The bot token or None on failure.
        """
        logger.info("Starting the process of creating a new bot...")

        async with self._app.conversation('@BotFather') as conv:
            try:
                await conv.send_message("/cancel")
            except errors.UserIsBlockedError:
                await self._app(UnblockRequest('@BotFather'))

            await conv.get_response()

            await conv.send_message("/newbot")
            response = await conv.get_response()

            if any(
                phrase in response.text
                for phrase in ["That I cannot do.", "Sorry"]
            ):
                if 'too many attempts' in response.text:
                    seconds = response.text.split()[-2]
                    logger.error(f'Please try again after {seconds} seconds')
                elif '20 bots' in response.text:
                    logger.error("You have 20 bots, please delete one of your bots to continue")
                else:
                    logger.error("An error occurred while creating the bot. @BotFather's response:")
                    logger.error(response.text)

                return sys.exit(0)


            await conv.send_message(f"Teagram UserBot of {utils.get_display_name(self._manager.me)[:45]}")
            await conv.get_response()
            
            bot_username = f"teagram_{utils.random_id(6)}_bot"

            await conv.send_message(bot_username)

            time.sleep(0.5)
            response = await conv.get_response()

            search = re.search(r"(?<=<code>)(.*?)(?=</code>)", response.text)
            if not search and not (search := re.search(
                r"\d{1,}:[0-9a-zA-Z_-]{35}",
                response.text
            )):
                logger.error("An error occurred while creating the bot. @BotFather's response:")
                return logger.error(response.text)

            token = search.group(0)

            await conv.send_message("/setuserpic")
            await conv.get_response()

            await conv.send_message(f"@{bot_username}")
            await conv.get_response()

            await conv.send_file("assets/teagram_bot.png")
            await conv.get_response()
            
            for message in [
                "/setinline",
                f"@{bot_username}",
                "teagram-command",
                "/setinlinefeedback",
                f"@{bot_username}",
                "Enabled"
            ]:
                await conv.send_message(message)
                await conv.get_response()

                await asyncio.sleep(1)

            logger.info("Bot created successfully")
            return token

    async def _revoke_token(self) -> str:
        """
        Revoke a bot token.
        
        Returns:
            str: The revoked bot token.
        """
        async with self._app.conversation("@BotFather") as conv:
            try:
                await conv.send_message("/cancel")
            except errors.UserIsBlockedError:
                await self._app(UnblockRequest('@BotFather'))

            await conv.get_response()

            await conv.send_message("/revoke")
            response = await conv.get_response()

            if "/newbot" in response.text:
                return logger.error("No created bots")

            if not response.reply_markup:
                logger.warning('reply_markup not found')
                time.sleep(1.5)
                response = await conv.get_response()

            if not getattr(response.reply_markup, 'rows', None):
                logger.warning('Retrying (CTRL + Z/C to stop)')
                await self._revoke_token()

            found = False
            for row in response.reply_markup.rows:
                for button in row.buttons:
                    if search := re.search(
                        r"@teagram_[0-9a-zA-Z]{6}_bot", button.text
                    ):
                        self.bot_username = button.text

                        await conv.send_message(button.text)
                        found = True
                        break

                if found:
                    break
                else:
                    return False

            time.sleep(1)
            response = await conv.get_response()
            if search := re.search(r"\d{1,}:[0-9a-zA-Z_-]{35}", response.text):
                return str(search.group(0))
            token = response.text.split()[-1]
            return str(token)
