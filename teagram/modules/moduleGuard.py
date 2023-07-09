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
                {"id": "session", "name": "plugin can get session"},
                {"id": "config.ini", "name": "plugin can get auth data (config.ini)"}
            ],
            "info": [
                {"id": "other", "name": "other"},
                {"id": "other", "name": "other"}
            ]
        }

        basic_plugins = ['eval.py', 'example.py', 'help.py', 
                         'info.py', 'loader.py', 'moduleGuard.py',
                         'terminal.py', 'tester.py', 'translator.py',
                         'updater.py']
                         
        critical = []
        warns = []
        info = []
        file_list = os.listdir("teagram/modules/")

        for file_name in file_list:
            if file_name in basic_plugins:
                continue
            else:
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
        basic_text = """
<code>🍵teagram | UserBot</code>
<b>ModuleGuard</b>
"""
        for file_name in file_list:
            if not file_name.endswith('.py'):
                continue
            if file_name in basic_plugins:
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
        
        if message_text == basic_text:
            message_text += 'Подозрительных плагинов не найдено'

        await message.send_message("me", message_text)