import psutil
import os
import contextlib
import time
from pyrogram import Client, types
from datetime import timedelta
from .. import __version__, loader, utils

@loader.module(name="UserBot", author='teagram')
class AboutMod(loader.Module):
    """Узнайте что такое юзербот, или информацию о вашем 🍵teagram"""
    boot_time = time.time()
    
    async def info_cmd(self, app: Client, message: types.Message):
        """Информация о вашем 🍵teagram."""
        platform = ""
        IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
        IS_CODESPACES = "CODESPACES" in os.environ
        IS_DOCKER = "DOCKER" in os.environ
        IS_GOORM = "GOORM" in os.environ
        IS_WSL = False
        with contextlib.suppress(Exception):
            from platform import uname
            if "microsoft-standard" in uname().release:
                IS_WSL = True

        if IS_TERMUX:
            platform = "📱 Termux"
        elif IS_CODESPACES:
            platform = "👨‍💻 Github Codespaces"
        elif IS_DOCKER:
            platform = "🐳 Docker"
        elif IS_GOORM:
            platform = "💚 Goorm"
        elif IS_WSL:
            platform = "🧱 WSL"
        else:
            platform = "🖥️ VDS"
        await utils.answer(message, "☕")
        me: types.User = await app.get_me()
        uptime_raw = round(time.time() - self.boot_time)

        uptime = (timedelta(seconds=uptime_raw))
        
        await utils.answer(
            message,
            f"""
<b>💎 Владелец</b>:  `{me.username}`
<b>💻 Версия</b>:  `v{__version__}`

<b>🧠 CPU</b>:  `{utils.get_cpu()}%`
<b>💾 RAM</b>:  `{utils.get_ram()}MB`

<b>🕒 Аптайм</b>:  `{uptime}`

<b>{platform}</b>
""")
        
    async def ubinfo_cmd(self, app: Client, message: types.Message, args: str):
        """Информация о UserBot"""
        await utils.answer(message, "☕")
        await utils.answer(message, '''🤔 <b>Что такое юзербот?</b>
        
📚 <b>Юзербот это</b> - <b>Сборник разных програм</b> для взаймодeйствия с Telegram API
А с помощью взаймодействия с Telegram API <b>можно написать разныe скрипты</b> для автоматизаций некоторых действий со стороны пользователя такие как: <b>Присоединение к каналам, отправление сообщений, и т.д</b>

🤔 <b>Чем отличается юзербот от обычного бота?</b>

🤭 <b>Юзербот может выполняться на аккаунте обычного пользователя</b>
Например: @paveldurov А бот может выполняться только на специальных бот аккаунтах например: @examplebot
<b>Юзерботы довольно гибкие</b> в плане настройки, у них больше функций.

🛑 <b>Поддерживаются ли оффициально юзерботы телеграмом?</b>

🚫 <b>Нет.</b> Они оффициально не поддерживаются, но вас не заблокируют за использование юзерботов.
Но <b>могут заблокировать в случае выполнения вредоносного кода или за злоупотребление Telegram API</b> на вашем аккаунте, так что владельцу юзербота надо тщательно проверять что выполняется на вашем аккаунте.''')

    async def teagram_cmd(self, app: Client, message: types.Message, args: str):
        '''Узнать версию pyrogram'''
        await utils.answer(message,f"🔥 <b>Версия Pyrogram:</b> <code>{pyrogram.__version__}</code>")