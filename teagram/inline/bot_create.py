from core import _db, client

class inline:
    def bot_create(self):
        try:
            client.send_message("BotFather", "/cancel")
        except errors.UserIsBlocked:
            client.unblock_user("BotFather")
        me = app.get_me()
        commands = [
          "/newbot",
          f"🍵 UB - teagram of {me.username}",
          f"@teagram_{mr.username}_bot",
          "/setinline",
          f"@teagram_{me.username}_bot"
          f"teagram@{me.username}> ",
          "/setinlinefeedback",
          f"@teagram_{me.username}_bot",
          "Enabled"
        ]
        for command in commands:
            client.send_message("BotFather", command)