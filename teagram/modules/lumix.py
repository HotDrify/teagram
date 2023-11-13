import aiohttp
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
        self.api = "http://lumix.myddns.me:5810"

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
        
        data = {"module": args.split()[0]}

        await utils.answer(
            message,
            self.strings("searching")
        )
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(
                f"{self.api}/search", 
                params=data,
                headers={
                    "User-Agent": "Teagram-TL-Lumix",
                    "X-Lumix": "Lumix"
                }
            ) as response:
                text = await response.text()
        
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