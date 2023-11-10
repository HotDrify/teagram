#                            ██╗████████╗███████╗██╗░░░░░░█████╗░██╗░░░██╗███████╗
#                            ██║╚══██╔══╝╚════██║██║░░░░░██╔══██╗╚██╗░██╔╝╚════██║
#                            ██║░░░██║░░░░░███╔═╝██║░░░░░███████║░╚████╔╝░░░███╔═╝
#                            ██║░░░██║░░░██╔══╝░░██║░░░░░██╔══██║░░╚██╔╝░░██╔══╝░░
#                            ██║░░░██║░░░███████╗███████╗██║░░██║░░░██║░░░███████╗
#                            ╚═╝░░░╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
#                                            https://t.me/itzlayz
#                           
#                                    🔒 Licensed under the GNU AGPLv3
#                                 https://www.gnu.org/licenses/agpl-3.0.html

import telethon
import time

from .terminal import bash_exec
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue
from ..bot import BotManager

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto

from telethon.tl.custom import Message
from datetime import timedelta

@loader.module(name="info", author='teagram')
class InfoMod(loader.Module):
    """Узнайте что такое юзербот, или информацию о вашем 🍵teagram"""
    strings = {'name': 'info'}

    def __init__(self):
        self.boot_time = time.time()
        self.config = Config(
            ConfigValue(
                option='customText',
                default='',
                value=self.db.get('info', 'customText', ''),
                validator=validators.String(),
                doc="Ключевые слова: cpu, ram, tele, owner, uptime, version, platform"
            ),
            ConfigValue(
                option='customImage',
                doc='',
                default='',
                value=self.db.get('info', 'customImage', ''),
                validator=validators.String()
            )
        )
        self.bot: BotManager = self.bot

    async def info_inline_handler(self, inline):
        platform = utils.get_platform()
        uptime = timedelta(seconds=round(time.time() - utils._init_time))
        
        last = utils.git_hash()
        now = str(await bash_exec('git rev-parse HEAD')).strip()
        version = f'v{__version__}' + (' '+self.strings('update') if last != now else "")

        me = (await self.client.get_me()).username

        default = f"""
<b>💎 {self.strings('owner')}</b>:  <code>{me}</code>
<b>🐧 {self.strings('version')}</b>:  <code>{version}</code> (<a href="https://github.com/itzlayz/teagram-tl/commit/{last}">{last[:7]}</a>)

<b>🧠 CPU</b>:  <code>{utils.get_cpu()}%</code>
<b>📀 RAM</b>:  <code>{utils.get_ram()}MB</code>

<b>⌚ {self.strings('uptime')}</b>:  <code>{uptime}</code>
<b>📱 {self.strings('version')} telethon: <code>{telethon.__version__}</code></b>

<b>{platform}</b>
"""
        davatar = 'https://github.com/itzlayz/teagram-tl/blob/main/assets/bot_avatar.png?raw=true'

        custom = self.config.get('customText')
        avatar = self.config.get('customImage')

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
                    thumb_url=avatar or davatar,
                    photo_url=avatar or davatar,
                    caption=default or custom,
                    reply_markup=InlineKeyboardMarkup().row(
                        InlineKeyboardButton('❓ Teagram', url='https://t.me/UBteagram'),
                        InlineKeyboardButton('🤖 Github', url='https://github.com/itzlayz/teagram-tl')
                    )
                )
            ]
        )
    
    async def info_cmd(self, message: Message):
        """Информация о вашем 🍵teagram."""
        await self.bot.invoke_unit('info', message)