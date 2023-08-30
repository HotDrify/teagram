from telethon import TelegramClient, types
from .. import __version__, loader, utils

@loader.module(name="Help", author='teagram')
class HelpMod(loader.Module):
    """Помощь по командам 🍵 teagram"""

    async def help_cmd(self, message: types.Message, args: str):
        """Список всех модулей"""
        try:
            self.bot_username = '@' + (await self.bot.bot.get_me()).username
        except:
            self.bot_username = "Произошла ошибка, перезагрузите бота"

        if not args:
            text = ""
            for module in sorted(self.manager.modules, key=lambda mod: len(str(mod))):
                if module.name.lower() == 'help':
                    continue

                commands = " <b>|</b> ".join(
                    f"<code>{command}</code>" for command in module.command_handlers
                )

                inline = " <b>| 🤖</b>: " if module.inline_handlers else ""
                inline += " <b>|</b> ".join(
                    f"<code>{inline_command}</code>" for inline_command in module.inline_handlers
                )

                if commands or inline:
                    text += f"\n<b>{module.name}</b> - " + (commands if commands else '<b>Команд не найдено</b>') + inline

            modules_count = len(self.manager.modules) - 1
            bot_inline_info = f"<emoji id=5228968570863496802>🤖</emoji> Инлайн бот: <b>{self.bot_username}</b>\n"

            return await utils.answer(
                message, 
                f"<emoji id=5359370246190801956>☕️</emoji> Доступные модули <b>{modules_count}</b>\n{bot_inline_info}{text}"
            )

        module = self.manager.get_module(args)
        if not module:
            return await utils.answer(
                message, "<b><emoji id=5465665476971471368>❌</emoji> Такого модуля нет</b>")

        prefix = self.db.get("teagram.loader", "prefixes", ["."])[0]

        command_descriptions = "\n".join(
            f"👉 <code>{prefix + command}</code>\n"
            f"    ╰ {(module.command_handlers[command].__doc__ or 'Нет описания для команды').strip()}"
            for command in module.command_handlers
        )

        inline_descriptions = "\n".join(
            f"👉 <code>@{self.bot_username + ' ' + command}</code>\n"
            f"    ╰ {(module.inline_handlers[command].__doc__ or 'Нет описания для команды').strip()}"
            for command in module.inline_handlers
        )

        header = (
            f"<emoji id=5361735750968679136>🖥</emoji> <b>{module.name}</b>\n" +
            (f"<emoji id=5224695503605735506>🧑‍💻</emoji> Автор: <b>{module.author}</b>\n" if module.author else "") +
            (f"<emoji id=5224695503605735506>⌨️</emoji> Версия: <b>{module.version}</b>\n" if module.version else "") +
            (f"\n<emoji id=5400093244895797589>📄</emoji> Описание:\n    ╰ {module.__doc__ or 'Нет описания для модуля'}\n\n")
        )

        return await utils.answer(
            message, header + command_descriptions + "\n" + inline_descriptions
        )
