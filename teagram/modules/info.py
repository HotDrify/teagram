import pyrogram
import time

from .terminal import bash_exec
from pyrogram import Client, types
from datetime import timedelta
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue


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
                validators.String()
            ) # type: ignore
        )
    
    async def info_cmd(self, app: Client, message: types.Message):
        """Информация о вашем 🍵teagram."""
        platform = utils.get_platform()

        uptime_raw = round(time.time() - self.boot_time)
        uptime = (timedelta(seconds=uptime_raw))
        
        last = str(await bash_exec('git log -1')).split()[1].strip()
        now = str(await bash_exec('git rev-parse HEAD')).strip()
        version = f'`v{__version__}`' + (' <b>Доступно обновление</b>' if last != now else "")

        me = (await app.get_me()).username

        default = f"""
<b><emoji id=5471952986970267163>💎</emoji> Владелец</b>:  `{me}`
<b><emoji id=6334741148560524533>🆔</emoji> Версия</b>:  {version}

<b><emoji id=5357480765523240961>🧠</emoji> CPU</b>:  `{utils.get_cpu()}%`
<b>💾 RAM</b>:  `{utils.get_ram()}MB`

<b><emoji id=5974081491901091242>🕒</emoji> Аптайм</b>:  `{uptime}`
<b><emoji id=5377399247589088543>🔥</emoji> Версия pyrogram: `{pyrogram.__version__}`</b>

<b>{platform}</b>
"""

        text = default
        custom = self.config.get('customText')

        if custom:
            custom = custom.format(
                me=me,
                version=version,
                uptime=uptime,
                platform=platform
            )
        
        await utils.answer(
            message,
            custom or text
        )
        
    async def teagram_cmd(self, app: Client, message: types.Message, args: str):
        """Информация о UserBot"""
        await utils.answer(message, "☕")
        await utils.answer(message, '''<emoji id=5467741625507651028>🤔</emoji> <b>Что такое юзербот?</b>
        
<emoji id=5373098009640836781>📚</emoji> <b>Юзербот это</b> - <b>Сборник разных програм</b> для взаймодeйствия с Telegram API
А с помощью взаймодействия с Telegram API <b>можно написать разныe скрипты</b> для автоматизаций некоторых действий со стороны пользователя такие как: <b>Присоединение к каналам, отправление сообщений, и т.д</b>

<emoji id=6325536273435986182>🤔</emoji> <b>Чем отличается юзербот от обычного бота?</b>

🤭 <b>Юзербот может выполняться на аккаунте обычного пользователя</b>
Например: @paveldurov А бот может выполняться только на специальных бот аккаунтах например: @examplebot
<b>Юзерботы довольно гибкие</b> в плане настройки, у них больше функций.

<emoji id=5467596412663372909>⁉️</emoji> <b>Поддерживаются ли оффициально юзерботы телеграмом?</b>

<emoji id=5462882007451185227>🚫</emoji> <b>Нет.</b> Они оффициально не поддерживаются, но вас не заблокируют за использование юзерботов.
Но <b>могут заблокировать в случае выполнения вредоносного кода или за злоупотребление Telegram API</b> на вашем аккаунте, так что владельцу юзербота надо тщательно проверять что выполняется на вашем аккаунте.''')
