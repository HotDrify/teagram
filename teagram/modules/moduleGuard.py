from pyrogram import Client, types
from .. import loader, utils

import os

@loader.module(name="ModuleGuard", author='teagram')
class ModuleGuardMod(loader.Module):
    """moduleGuard оповестит вас о вредоносном модуле."""
    async def on_load(self, message: types.Message):
        names = {
            "info": [
                {"id": "other", "name": "other"},
                {"id": "other", "name": "other"}
            ],
            "warns": [
                {"id": "eval", "name": "Eval"},
                {"id": "exec", "name": "Exec"}
            ],
            "criticals": [
                {"id": "session", "name": "plugin can get session"},
                {"id": "config.ini", "name": "plugin can get auth data (config.ini)"}
            ]
        }

        basic_plugins = ['eval.py', '_example.py', 'help.py', 
                         'info.py', 'loader.py', 'moduleGuard.py',
                         'terminal.py', 'tester.py', 'translator.py',
                         'updater.py', 'backup.py']
                         
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
                        try:
                            content = file.read()
                        except UnicodeDecodeError:
                            continue


                    for word in names["warns"]:
                        if word['id'] in content:
                            warns.append(word["name"])

                    for word in names["criticals"]:
                        if word['id'] in content:
                            critical.append(word["name"])

                    # for word in names["info"]:
                    #     if word['id'] in content:
                    #         info.append(word["name"])

        message_text = """
<b>ModuleGuard</b>
"""
        basic_text = """
<b>ModuleGuard</b>
"""
        for file_name in file_list:
            if not file_name.endswith('.py'):
                continue
            if file_name in basic_plugins:
                continue
            else:
                info_text = ', '.join(info)
                warns_text = ', '.join(warns)
                critical_text = ', '.join(critical)
                message_text += f"{file_name}:\n"

                if info_text:
                    message_text += f"❔ Info ➜ {info_text}\n"
                if warns_text:
                    message_text += f"❗ Warns ➜ {warns_text}\n"
                if critical_text:
                    message_text += f"❌ Criticals ➜ {critical_text}\n"

                if not info and not warns and not critical:
                    message_text += 'Безопасный плагин ✔\n'
        
        if message_text == basic_text:
            message_text += 'Подозрительных плагинов не найдено'

        await message.send_message("me", message_text)
