import logging
import time

from pyrogram.methods.utilities.idle import idle

from . import auth, database, loader


async def main():
    """Основной цикл юзербота"""
    me, app = await auth.Auth().authorize()
    await app.initialize()

    db = database.db
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
