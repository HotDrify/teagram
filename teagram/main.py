from . import auth, database, loader, __version__
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest
from telethon.types import ChatAdminRights

from aiogram import Bot
import os, sys, atexit, time, logging

logger = logging.getLogger()

async def sendbot(bot: Bot, db, prefix: str, app):
    try:
        await bot.send_message(
            db.cloud.input_chat,
            '☕ <b>Teagram userbot has started!</b>\n'
            f'🤖 <b>Version: {__version__}</b>\n'
            f'❔ <b>Prefix: {prefix}</b>',
        )

        try:
            with open('teagram.log', 'r') as log:
                log = log.read()

                await bot.send_message(
                    db.cloud.input_chat,
                    f'📁 <b>Logs</b>\n<code>{log}</code>'
                )
        except:
            pass
    except:
        id = (await bot.get_me()).id
        admin = ChatAdminRights(
            post_messages=True,
            ban_users=True,
            edit_messages=True,
            delete_messages=True
        )

        await app(InviteToChannelRequest(
            db.cloud.input_chat,
            [id]
        ))

        await app(EditAdminRequest(
            db.cloud.input_chat,
            id, 
            admin,
            'Teagram'
        ))

        await bot.send_message(
            db.cloud.input_chat,
            f'☕ <b>Teagram userbot has started!</b>\n🤖 <b>Version: {__version__}</b>\n❔ <b>Prefix: {prefix}</b>',
        )

async def main():
    db = database.db

    if (app := auth.Auth(manual=False).app):
        await app.connect()
        if not (me := await app.get_me()):
            if db.get('teagram.loader', 'web_success', ''):
                db.pop('teagram.loader', 'web_success')
                
                me, app = await auth.Auth().authorize()
                await app.connect()
            else:
                if db.get('teagram.loader', 'web_auth', '') is False:
                    inpt = 'yes'
                else:
                    inpt = input('Use web? (y/n): ')
                    if not inpt:
                        inpt = 'n'
                    
                if inpt.lower() in ['y', 'yes', 'ye']:
                    db.set('teagram.loader', 'web_auth', True)
                    def restart():
                        os.execl(sys.executable, sys.executable, "-m", "teagram")

                    atexit.register(restart)
                    sys.exit(1)
                else:
                    me, app = await auth.Auth().authorize()
                    await app.connect()
    
    db.init_cloud(app, me)
    await db.cloud.get_chat()
    
    modules = loader.ModulesManager(app, db, me)
    bot: Bot = await modules.load(app)

    prefix = db.get("teagram.loader", "prefixes", ["."])[0]
    restart = db.get("teagram.loader", "restart")
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

        lang = db.get('teagram.loader', 'lang', '')
        # if there was no lang in db
        if not lang:
            lang = 'en'
            db.set('teagram.loader', 'lang', 'en')

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
            await sendbot(bot, db, prefix, app)

        db.pop("teagram.loader", "restart")
    else:
        await sendbot(bot, db, prefix, app)

    await app.run_until_disconnected()
