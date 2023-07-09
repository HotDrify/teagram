from pyrogram import Client, types
from .. import loader, utils

import os

@loader.module(name="ModuleGuard")
class ModuleGuardMod(loader.Module):
    """moduleGuard оповестит вас о вредоносном модуле."""
    async def on_load(self, message: types.Message):
        names = {
            "warns": [
                {"id": "eval", "name": "Eval"},
                {"id": "exec", "name": "Exec"}
            ],
            "critical": [
                {"id": "other", "name": "other"},
                {"id": "other", "name": "other"}
            ],
            "info": [
                {"id": "other", "name": "other"},
                {"id": "other", "name": "other"}
            ]
        }

        critical = []
        warns = []
        info = []
        file_list = os.listdir("teagram/modules/")

        for file_name in file_list:
            if 'moduleGuard' in file_name:
                continue
            else:
                file_path = os.path.join("teagram/modules/", file_name)
                if os.path.isfile(file_path):
                    with open(file_path, "r") as file:
                        content = file.read()
                    for word in names["warns"]:
                        if word['id'] in content:
                            warns.append(word["name"])
                    for word in names["critical"]:
                        if word['id'] in content:
                            critical.append(word["name"])
                    for word in names["info"]:
                        if word['id'] in content:
                            info.append(word["name"])

        message_text = """
<code>🍵teagram | UserBot</code>
<b>ModuleGuard</b>
"""
        for file_name in file_list:
            if 'moduleGuard' in file_name:
                continue
            else:
                warns_text = ', '.join(warns)
                critical_text = ', '.join(critical)
                info_text = ', '.join(info)
                message_text += f"{file_name}:\n"
                message_text += f"warns ➜ {warns_text}\n"
                message_text += f"criticals ➜ {critical_text}\n"
                message_text += f"info ➜ {info_text}\n"

        await message.send_message("me", message_text)