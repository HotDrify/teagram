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
            "criticals": [
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
                if file_name.endswith('.py'):
                    file_path = os.path.join("teagram/modules/", file_name)
                    if os.path.isfile(file_path):
                        with open(file_path, "r") as file:
                            content = file.read()
                        for word in names["warns"]:
                            if word['id'] in content:
                                warns.append(word["name"])
                        for word in names["criticals"]:
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
                if warns_text:
                    message_text += f"warns ➜ {warns_text}\n"
                if critical_text:
                    message_text += f"criticals ➜ {critical_text}\n"
                if info_text:
                    message_text += f"info ➜ {info_text}\n"

        await message.send_message("me", message_text)