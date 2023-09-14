from loguru import logger
import time

from . import auth, database, loader, utils

import os, sys, atexit

async def main():
    """Основной цикл юзербота"""
    db = database.db

    if db.get('teagram.loader', 'web_success', ''):
        me, app = await auth.Auth().authorize()
        await app.connect()
    else:
        inpt = input('Web or manual (y/n): ')
        if not inpt:
            inpt = 'n'
            
        if inpt.lower() in ['y', 'yes', 'ye'] and (
            'windows' in (pl := utils.get_platform().lower()) or 'wsl' in pl
        ):
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
    print(
"""

  _____ _____    _    ____ ____      _    __  __ 
 |_   _| ____|  / \  / ___|  _ \    / \  |  \/  |
   | | |  _|   / _ \| |  _| |_) |  / _ \ | |\/| |
   | | | |___ / ___ \ |_| |  _ <  / ___ \| |  | |
   |_| |_____/_/   \_\____|_| \_\/_/   \_\_|  |_|


""")
    print('Юзербот включен (Префикс - "{}")'.format(prefix))
    
    

    if (restart := db.get("teagram.loader", "restart")):
        restarted_text = (
            f"<b>✅ Перезагрузка прошла успешно! ({round(time.time())-int(restart['start'])} сек.)</b>"
            if restart["type"] == "restart"
            else f"<b>✅ Обновление прошло успешно! ({round(time.time())-int(restart['start'])} сек.)</b>"
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
            await db.cloud.send_data(restarted_text)

        db.pop("teagram.loader", "restart")
    else:
        await db.cloud.send_data('Userbot has started (Prefix - "{}")'.format(prefix))

    await app.run_until_disconnected()

    logger.info("Завершение работы...")
    return True
