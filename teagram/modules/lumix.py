#                            ██╗████████╗███████╗██╗░░░░░░█████╗░██╗░░░██╗███████╗
#                            ██║╚══██╔══╝╚════██║██║░░░░░██╔══██╗╚██╗░██╔╝╚════██║
#                            ██║░░░██║░░░░░███╔═╝██║░░░░░███████║░╚████╔╝░░░███╔═╝
#                            ██║░░░██║░░░██╔══╝░░██║░░░░░██╔══██║░░╚██╔╝░░██╔══╝░░
#                            ██║░░░██║░░░███████╗███████╗██║░░██║░░░██║░░░███████╗
#                            ╚═╝░░░╚═╝░░░╚══════╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
#                                            https://t.me/itzlayz
#                           
#                                    🔒 Licensed under the GNU AGPLv3
#                                 https://www.gnu.org/licenses/agpl-3.0.html

import requests
from .. import loader, utils

@loader.module("Lumix", "itzlayz", 1.0)
class LumixMod(loader.Module):
    strings = {
        "name": "Lumix",
        "searching": "🔎 <b>Searching module</b>",
        "installed": "✅ <b>Module successfully loaded</b>\n",
        "not_found": "❌ <b>Module not found</b>",
        "installing": "📥 <b>Installing module</b>"
    }
    strings_ru = {
        "name": "Lumix",
        "searching": "🔎 <b>Поиск модуля</b>",
        "installed": "✅ <b>Модуль успешно установлен</b>\n",
        "not_found": "❌ <b>Модуль не найден</b>",
        "installing": "📥 <b>Устанавливаем модуль</b>"
    }
    def __init__(self):
        self.api = "http://lumix.myddns.me:5810/"

    def prep_docs(self, module: str) -> str:
        module = self.lookup(module)
        prefix = self.get_prefix()[0]
        return "\n".join(
            f"""👉 <code>{prefix + command}</code> {f"- <b>{module.command_handlers[command].__doc__}</b>" or ''}"""
            for command in module.command_handlers
        )

    @loader.command()
    async def lumix(self, message, args: str):
        if not args:
            return await utils.answer(
                message,
                self.strings("not_found")
            )

        await utils.answer(
            message,
            self.strings("searching")
        )

        text = (await utils.run_sync(
            requests.get, 
            f"{self.api}/view/{args.split()[0]}",
        )).text
        
        if text == "Not found":
            return await utils.answer(
                message,
                self.strings("not_found")
            )
        
        await utils.answer(
            message,
            self.strings("installing")
        )
        
        name = await self.manager.load_module(text)
        await utils.answer(
            message,
            self.strings("installed").format(name) + self.prep_docs(name)
        )
