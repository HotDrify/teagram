import logging
import time

from telethon import TelegramClient
from . import auth, database, loader


async def main():
    """Основной цикл юзербота"""
    me, app = await auth.Auth().authorize()
    app: TelegramClient
    await app.connect()

    db = database.db
    db.init_cloud(app, me)

    modules = loader.ModulesManager(app, db, me)
    await modules.load(app)

    prefix = db.get("teagram.loader", "prefixes", ["."])[0]
    
    print('Юзербот включен (Префикс - "{}")'.format(prefix))
    print(
"""

  _____ _____    _    ____ ____      _    __  __ 
 |_   _| ____|  / \  / ___|  _ \    / \  |  \/  |
   | | |  _|   / _ \| |  _| |_) |  / _ \ | |\/| |
   | | | |___ / ___ \ |_| |  _ <  / ___ \| |  | |
   |_| |_____/_/   \_\____|_| \_\/_/   \_\_|  |_|


"""
    )

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

    logging.info("Завершение работы...")
    return True
