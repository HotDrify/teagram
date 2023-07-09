from pyrogram import Client, types
from .. import loader, utils

import os

@loader.module(name="ModuleGuard")
class ModuleGuardMod(loader.Module):
    """moduleGuard оповестит вас о вредоносном модуле."""
    async def on_load(self, message: types.Message):
        names = {
            "warning": [
              {"id": "subprocess", "name": "commands exec"},
              {"id": "eval", "name": "exec python code"},
              {"id": "exec", "name": "exec python code"}
            ],
            "info": [],
            "critical": [
                {"id": "telethon", "name": "other telegram client"},
                {"id": "get_me", "name": "get your profile account data"},
                {"id": "GetAuthorizationsRequest", "name": "get account auth data"},
                {"id": "sessions", "name": "get sessions data"},
                {"id": "exit", "name": "stop bot script"},
                {"id": "config.ini", "name": "access to authorization config"}
            ]
        }
        critical = []
        warning = []
        info = []
        file_list = os.listdir("teagram/modules/")

        for file_name in file_list:
            file_path = os.path.join("teagram/modules/", file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                for word in names["warning"]:
                    if word['id'] in content:
                        warning.append({"file": file_name, "found": word["name"]})
                for word in names["critical"]:
                    if word['id'] in content:
                        critical.append({"file": file_name, "found": word["name"]})

        message_text = """
<code>🍵teagram | UserBot</code>
<b>ModuleGuard</b>
Найдено:
"""
        for item in warning:
            message_text += f"WARNING | File: {item['file']}, Found: {item['found']}\n"
        await message.send_message("me", message_text)