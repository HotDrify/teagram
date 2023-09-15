import logging
import time
import os, sys, atexit

from pyrogram.methods.utilities.idle import idle

from . import auth, database, loader

async def main():
    """Основной цикл юзербота"""
    db = database.db
    if (app := auth.Auth(manual=False).app):
        await app.connect()
        try:
            me = await app.get_me()
        except:
            me = False
            
        if not me:
            if db.get('teagram.loader', 'web_success', ''):
                db.pop('teagram.loader', 'web_success')
                
                me, app = await auth.Auth().authorize()
                await app.connect()
            else:
                if db.get('teagram.loader', 'web_auth', '') is False:
                    inpt = 'yes'
                else:
                    inpt = input('Web or manual (y/n): ')
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

    modules = loader.ModulesManager(app, db, me)
    await modules.load(app)

    prefix = db.get("teagram.loader", "prefixes", ["."])[0]
    print('Юзербот включен (Префикс - "{}")'.format(prefix))

    if (restart := db.get("teagram.loader", "restart")):
        restarted_text = (
            f"✅ Перезагрузка прошла успешно! ({round(time.time())-int(restart['start'])} сек.)"
            if restart["type"] == "restart"
            else f"✅ Обновление прошло успешно! ({round(time.time())-int(restart['start'])} сек.)"
        )
        
        try:
            msg = await app.get_messages(*map(int, restart["msg"].split(":")))
            if (
                not msg.empty
                and msg.text != (
                    restarted_text
                )
            ):
                await msg.edit(restarted_text)
        except:
            print(restarted_text)

        db.pop("teagram.loader", "restart")

    await idle()

    logging.info("Завершение работы...")
    return True
