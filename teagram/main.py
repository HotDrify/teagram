import logging

from pyrogram.methods.utilities.idle import idle

from . import auth, database, loader


async def main():
    """Основной цикл юзербота"""
    try:
        me, app = await auth.Auth().authorize()
    except TypeError:
        return print('Пожалуйста перезапустите модуль ')
    
    await app.initialize()

    db = database.db
    db.init_cloud(app, me)

    modules = loader.ModulesManager(app, db, me)
    await modules.load(app)

    if (restart := db.get("teagram.loader", "restart")):
        msg = await app.get_messages(*map(int, restart["msg"].split(":")))
        if (
            not msg.empty
            and msg.text != (
                restarted_text := (
                    "✅ Перезагрузка прошла успешно!"
                    if restart["type"] == "restart"
                    else "✅ Обновление прошло успешно!"
                )
            )
        ):
            await msg.edit(restarted_text)

        db.pop("teagram.loader", "restart")

    prefix = db.get("teagram.loader", "prefixes", ["."])[0]

    await idle()

    logging.info("Завершение работы...")
    return True
