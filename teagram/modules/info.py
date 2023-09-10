import telethon
import time

from .terminal import bash_exec
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue
from ..bot import BotManager

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto, InputTextMessageContent

from telethon.tl.custom import Message
from datetime import timedelta

@loader.module(name="UserBot", author='teagram')
class AboutMod(loader.Module):
    """Узнайте что такое юзербот, или информацию о вашем 🍵teagram"""
    strings = {'name': 'info'}

    def __init__(self):
        self.boot_time = time.time()
        self.config = Config(
            ConfigValue(
                option='customText',
                default='',
                value=self.db.get('UserBot', 'customText', ''),
                validator=validators.String(),
                docstring="Ключевые слова: cpu, raw, tele, owner, uptime, version, platform"
            ),
            ConfigValue(
                option='customImage',
                docstring='',
                default='',
                value=self.db.get('UserBot', 'customImage', ''),
                validator=validators.String()
            )
        )
        self.bot: BotManager = self.bot

    async def info_inline_handler(self, inline):
        platform = utils.get_platform()

        uptime_raw = round(time.time() - self.boot_time)
        uptime = (timedelta(seconds=uptime_raw))
        
        last = utils.git_hash()
        now = str(await bash_exec('git rev-parse HEAD')).strip()
        version = f'v{__version__}' + (' '+self.strings['update'] if last != now else "")

        me = (await self.client.get_me()).username

        default = f"""
<b>💎 {self.strings['owner']}</b>:  <code>{me}</code>
<b>🐧 {self.strings['version']}</b>:  <code>{version}</code> (<a href="https://github.com/itzlayz/teagram-tl/commit/{last}">{last[:7]}</a>)

<b>🧠 CPU</b>:  <code>{utils.get_cpu()}%</code>
<b>📀 RAM</b>:  <code>{utils.get_ram()}MB</code>

<b>⌚ {self.strings['uptime']}</b>:  <code>{uptime}</code>
<b>📱 {self.strings['version']} telethon: <code>{telethon.__version__}</code></b>

<b>{platform}</b>
"""

        custom = self.config.get('customText')
        avatar = self.config.get('customImage',
                     'https://github.com/itzlayz/teagram-tl/blob/main/assets/bot_avatar.png?raw=true')

        if custom:
            custom = custom.format(
                owner=me,
                cpu=utils.get_cpu(),
                ram=utils.get_ram(),
                uptime=uptime,
                version=version,
                platform=platform,
                tele=telethon.__version__
            )

        await inline.answer(
            [
                InlineQueryResultPhoto(
                    id=utils.random_id(),
                    title='teagram',
                    thumb_url=avatar,
                    photo_url=avatar,
                    caption=default or custom,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton('❓ Teagram', url='https://t.me/UBteagram')
                    ).add(
                        InlineKeyboardButton('🤖 Github', url='https://github.com/itzlayz/teagram-tl')
                    )
                )
            ]
        )
    
    async def info_cmd(self, message: Message):
        """Информация о вашем 🍵teagram."""
        await self.bot.invoke_unit('info', message)