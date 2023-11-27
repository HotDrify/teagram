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

from . import auth, database, loader, web, utils, __version__

from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest
from telethon.types import ChatAdminRights

from aiogram import Bot
import os, sys, git, time, logging

logger = logging.getLogger()
sys.modules['teagram.inline'] = sys.modules['teagram.bot']

class TeagramStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logs = {
            'INFO': [],
            'WARNING': [],
            'ERROR': [],
            'CRITICAL': [],
            'DEBUG': [],
            'NOTSET': []
        }

        with open("teagram.log", "w", encoding='utf-8') as l:
            l.write("")

    def emit(self, record):
        lvl = logging.getLevelName(record.levelno)
        self.logs[lvl].append(record)

        with open("teagram.log", "a", encoding='utf-8') as l:
            l.write(f'{self.format(record)}\n')
        
        super().emit(record)

class Main:
    def __init__(self, args) -> None:
        self.db = database.db
        self.args = args

        fmt = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        handler = TeagramStreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(fmt)

        self.log = logging.getLogger()
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

        logging.getLogger('telethon').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('aiogram').setLevel(logging.WARNING)
    
    async def inline(self, bot, app, db):
        id = dict(await bot.get_me())["id"]
        admin = ChatAdminRights(
            post_messages=True,
            ban_users=True,
            edit_messages=True,
            delete_messages=True
        )

        await app(
            InviteToChannelRequest(
                db.cloud.input_chat,
                [id]
            )
        )

        await app(
            EditAdminRequest(
                db.cloud.input_chat,
                id, 
                admin,
                'Teagram'
            )
        )

    async def on_start(self, 
                      bot: Bot, 
                      db: database.Database, 
                      prefix: str, app):
        _sha = git.Repo().rev_parse("HEAD")
        version = f"""<a href="{_sha}">{__version__}</a>"""

        try:
            await bot.send_photo(
                chat_id=db.cloud.input_chat,
                photo="https://raw.githubusercontent.com/itzlayz/teagram-tl/main/assets/teagram_banner.png",
                caption='☕ <b>Teagram userbot has started!</b>\n'
                f'🤖 <b>Version: {version}</b>\n'
                f'❔ <b>Prefix: {prefix}</b>'
            )

            with utils.supress(Exception):
                with open('teagram.log', 'r') as log:
                    log = log.readlines()
                    if len(log) > 1:
                        await bot.send_message(
                            db.cloud.input_chat,
                            f'📁 <b>Logs</b>\n<code>{log}</code>'
                        )
        except Exception:
            await self.inline(bot, app, db)

            await bot.send_photo(
                chat_id=db.cloud.input_chat,
                photo="https://raw.githubusercontent.com/itzlayz/teagram-tl/main/assets/teagram_banner.png",
                caption='☕ <b>Teagram userbot has started!</b>\n'
                f'🤖 <b>Version: {version}</b>\n'
                f'❔ <b>Prefix: {prefix}</b>'
            )

    async def main(self):
        try:
            if (
                os.geteuid() == 0
                and utils.get_platform() not in ["🐳 Docker"]
            ):
                self.log.warning("Please do not use root for userbot")
        except:
            pass

        app = auth.Auth(manual=False).app
        await app.connect()

        if (
            not getattr(self.args, 'disable_web', '') and 
            not await app.get_me()
        ):
            import socket
            from random import randint

            port = randint(1000, 65535)
            if 'windows' not in utils.get_platform().lower():
                while True:
                    port = randint(1000, 65535)
                    try:
                        with socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM
                        ) as sock:
                            sock.bind(("localhost", port))

                        break
                    except OSError as e:
                        if e.errno == 98:
                            continue

            web_config = web.Web(port)
            await web_config.server.serve()
            
            return
        
        await app.disconnect()

        me, app = await auth.Auth().authorize()
        self.db.init_cloud(app, me)
        await self.db.cloud.get_chat()
        
        modules = loader.ModulesManager(app, self.db, me)
        bot: Bot = await modules.load(app)
        
        self.modules = modules

        prefix = self.db.get("teagram.loader", "prefixes", ["."])[0]
        restart = self.db.get("teagram.loader", "restart")

        if not restart:
            print("""
▀▀█▀▀  █▀▀▀  █▀▀█  █▀▀█  █▀▀█  █▀▀█  █▀▄▀█ 
  █    █▀▀▀  █▄▄█  █ ▄▄  █▄▄▀  █▄▄█  █ █ █ 
  █    █▄▄▄  █  █  █▄▄█  █  █  █  █  █   █
            """)
            logger.info(f'Userbot has started! Prefix "{prefix}"')    

        if restart:
            restarted = round(time.time())-int(restart['start'])
            ru = (
                f"<b>✅ Перезагрузка прошла успешно! ({restarted} сек.)</b>"
                if restart["type"] == "restart"
                else f"<b>✅ Обновление прошло успешно! ({restarted} сек.)</b>"
            )
            en = (
                f"<b>✅ Reboot was successful! ({restarted} сек.)</b>"
                if restart["type"] == "restart"
                else f"<b>✅ The update was successful! ({restarted} сек.)</b>"
            )

            lang = self.db.get('teagram.loader', 'lang', '')
            # if there was no lang in db
            if not lang:
                lang = 'en'
                self.db.set('teagram.loader', 'lang', 'en')

            restarted_text = (
                ru 
                if lang == 'ru'
                else en
            )
            
            try:
                _id = list(map(int, restart["msg"].split(":")))
                msg = await app.get_messages(_id[0], ids=_id[1])

                if (
                    msg and msg.text != (
                        restarted_text
                    )
                ):
                    await app.edit_message(_id[0], _id[1], restarted_text, parse_mode='html')
            except:
                await self.on_start(bot, self.db, prefix, app)

            self.db.pop("teagram.loader", "restart")
        else:
            await self.on_start(bot, self.db, prefix, app)

        await app.run_until_disconnected()
