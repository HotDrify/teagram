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

    print('Юзербот включен ({})'.format(me.first_name))

    if (restart := db.get("teagram.loader", "restart")):
        msg = await app.get_messages(*map(int, restart["msg"].split(":")))
        if (
            not msg.empty
            and msg.text != (
                restarted_text := (
                    "✅ Перезагрузка прошла успешно!"
                    if restart["type"] == "restart"
                    else f"✅ Обновление прошло успешно! ({round(time.time())-int(restart['start'])} сек.)"
                )
            )
        ):
            await msg.edit(restarted_text)

        db.pop("teagram.loader", "restart")

    prefix = db.get("teagram.loader", "prefixes", ["."])[0]

    await idle()

    logging.info("Завершение работы...")
    return True
