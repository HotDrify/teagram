import telethon
import time

from .terminal import bash_exec
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue
from ..bot import BotManager

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from telethon.tl.custom import Message
from datetime import timedelta

@loader.module(name="UserBot", author='teagram')
class AboutMod(loader.Module):
    """Узнайте что такое юзербот, или информацию о вашем 🍵teagram"""
    def __init__(self):
        self.boot_time = time.time()
        self.config = Config(
            ConfigValue(
                'customText',
                '',
                self.db.get('UserBot', 'customText') or '',
                validators.String(),
                "Ключевые слова: cpu, raw, tele, owner, uptime, version, platform"
            ), # type: ignore
            ConfigValue(
                'customImage',
                '',
                self.db.get('UserBot', 'customImage') or '',
                validators.String()
            ) # type: ignore
        )
        self.bot: BotManager = self.bot
    
    async def info_cmd(self, message: Message):
        """Информация о вашем 🍵teagram."""
        platform = utils.get_platform()

        uptime_raw = round(time.time() - self.boot_time)
        uptime = (timedelta(seconds=uptime_raw))
        
        last = str(await bash_exec('git log -1')).split()[1].strip()
        now = str(await bash_exec('git rev-parse HEAD')).strip()
        version = f'v{__version__}' + (' <b>Доступно обновление</b>' if last != now else "")

        me = (await self.client.get_me()).username

        default = f"""
<b><emoji id=5471952986970267163>💎</emoji> Владелец</b>:  <code>{me}</code>
<b><emoji id=6334741148560524533>🐧</emoji> Версия</b>:  <code>{version}</code>

<b><emoji id=5357480765523240961>🧠</emoji> CPU</b>:  <code>{utils.get_cpu()}%</code>
<b>📀 RAM</b>:  <code>{utils.get_ram()}MB</code>

<b><emoji id=5974081491901091242>⌚</emoji> Аптайм</b>:  <code>{uptime}</code>
<b><emoji id=5377399247589088543>📱</emoji> Версия telethon: <code>{telethon.__version__}</code></b>

<b>{platform}</b>
"""

        custom = self.config.get('customText')
        custom_avatar = self.config.get('customImage')

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
        
        await utils.answer(
            message,
            custom_avatar or 'assets/bot_avatar.png',
            photo=True,
            caption=custom or default
        )