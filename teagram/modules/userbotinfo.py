from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="AboutUserBot")
class AboutUserBot(loader.Module):
    """Узнайте что такое юзербот"""
    
    async def ubcmd(self, app: Client, message: types.Message, args: str):
        """Вызвать информацию о том что такое юзербот(🍵 teagram)"""
        await utils.answer(message, "☕")
        await utils.answer(message,'''🤔 Что такое юзербот?
😚 Юзербот это - сборник разных програм для взаймодействия с Telegarm API
А с помощью взаймодействия с Telegarm API можно написать разные скрипты для автоматизаций некоторых действий со стороны пользователя такие как: Присоединение к каналам, отправление сообщений, и т.д

🤔 Чем отличается юзербот от обычного бота?

Юзербот может выполняться на аккаунте обычного человека 
Например: @pavel_durov А бот может выполняться только на специальных бот аккаунтах например: @examplebot
Юзерботы довольно гибкие в плане настройки, у них больше функций.

🛑 Поддерживаются ли оффициально юзерботы телеграмом?

🚫 Нет. Они оффициально не поддерживаются, но вас не заблокируют за использование юзерботов.
Но могут заблокировать в случае выполнения вредоносного кода на вашем аккаунте, так что владельцу юзербота надо тчательно проверять что выполняется на вашем аккаунте.''')
