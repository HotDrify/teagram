<p align="center">
    <img src="./assets/bot_avatar.png" width="500" alt="teagram-UB">
    <br>
    <b><a href="https://t.me/UBteagram">Teagram UserBot</a></b> — крутой юзербот написанный на <a href="https://github.com/pyrogram/pyrogram">Pyrogram</a>
    <br>
    <a href='https://github.com/hotdrify/teagram#установка'>
        Установка
    </a>
    |
    <a href='https://github.com/hotdrify/teagram#комьюнити'>
        Комьюнити
    </a>
    |
    <a href='https://github.com/hotdrify/teagram#пример-модуля'>
        Пример модуля
    </a>
</p>



<h1>Описание</h1>

Teagram — это ваш интерактивный многофункциональный помощник в Телеграме  
Многофункциональный и расширяемый юзербот позволит создавать любые модули, нужна лишь фантазия

Подключение к аккаунту происходит посредством создании новой (!) сессии

Наши преимущества:
<ul>
    <li>Удобство и простота в использовании</li>
    <li>Низкая ресурсозатраность</li>
    <li>Большой ассортимент готовых модулей</li>
    <li>Грамотное построение структуры каждого модуля</li>
    <li>Асинхронное выполнение каждой задачи</li>
    <li>Удобная загрузка и выгрузка модулей</li>
    <li>Инлайн бот</li>
</ul>

<h1>Установка</h1>
<h2>Termux(<a href='https://f-droid.org/en/packages/com.termux/'>f-droid</a>) / Linux / Windows WSL</h2>
<pre lang="bash">
apt update && apt upgrade -y && apt install -y openssl git python3 python3-pip
</pre>

После этого клонировать репозиторий и установить зависимости:

<pre lang="bash">
git clone https://github.com/HotDrify/teagram && cd teagram 
pip3 install -r requirements.txt
</pre>

> Также, вы можете установить необязательные зависимости для ускорения работы:

<pre lang="bash">
pip3 install -r requirements-speedup.txt
</pre>


<h1>Запуск</h1>

> При первом запуске потребуется ввести api_id и api_hash. Их можно получить на <a href="https://my.telegram.org">my.telegram.org</a>

<pre lang="bash">
python3 -m teagram
</pre>

<h1>Пример модуля</h1>

> Больше примеров функций и полное описание смотри в файле <a href="./teagram/modules/_example.py">_example.py</a>

<pre lang="python">
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="Example")
class ExampleMod(loader.Module): # Модуль обязательно должен заканчиваться на Mod
    """Описание модуля"""


    async def example_cmd(self, app: Client, message: types.Message, args: str):  # _cmd на конце функции чтобы обозначить команду
                                                                                  # args - аргументы после команды. необязательный аргумент
        """Описание команды. Использование: example [аргументы]"""
        await utils.answer(  # utils.answer - это отправка сообщений, код можно посмотреть в utils
            message, "Ого пример команды" + (
                f"\nАргументы: {args}" if args
                else ""
            )
        )


    @loader.on(lambda _, __, m: m and m.text == "Привет, это вотчер детка")
    async def watcher(self, app: Client, message: types.Message):  # watcher - функция которая работает при получении нового сообщения
        return await message.reply(
            "Привет, все работает отлично")
</pre>
<h1>Комьюнити</h1>
<b><a href="https://t.me/UBteagram">Telegram (RU/EN)</a></b>
<b><a href="https://discord.gg/s37xWt9Rr7">Discord (RU/EN)</a></b>