from pyrogram import Client, types

from .. import __version__, loader, utils


@loader.module(name="Help", author='teagram')
class HelpMod(loader.Module):
    """Помощь по командам 🍵 teagram"""
    async def help_cmd(self, app: Client, message: types.Message, args: str):
        """Список всех модулей"""
        self.bot_username = (await self.bot.bot.get_me()).username

        if not args:
            text = ""
            for module in sorted(self.all_modules.modules, key=lambda mod: len(str(mod))):
                if module.name.lower() == 'help':
                    continue

                commands = inline = ""

                commands += " <b>|</b> ".join(
                    f"<code>{command}</code>" for command in module.command_handlers
                )

                if module.inline_handlers:
                    if commands:
                        inline += " <b>|| [inline]</b>: "
                    else:
                        inline += "<b>[inline]</b>: "

                inline += " <b>|</b> ".join(
                    f"<code>{inline_command}</code>" for inline_command in module.inline_handlers
                )

                if not commands and not inline:
                    pass
                else:
                    text += f"\n<b>{module.name}</b> - " + (commands if commands else '`Команд не найдено`') + inline

            return await utils.answer(
                message, 
                f"🤖 Инлайн бот: <b>@{self.bot_username}</b>\n☕️ Доступные модули <b>{len(self.all_modules.modules)-1}</b>\n"
                f"{text}"
            )

        if not (module := self.all_modules.get_module(args)):
            return await utils.answer(
                message, "❌ Такого модуля нет")

        prefix = self.db.get("teagram.loader", "prefixes", ["."])[0]

        command_descriptions = "\n".join(
            f"👉 <code>{prefix + command}</code>\n"
            f"    ╰ {module.command_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in module.command_handlers
        )
        inline_descriptions = "\n".join(
            f"👉 <code>@{self.bot_username + ' ' + command}</code>\n"
            f"    ╰ {module.inline_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in module.inline_handlers
        )

        header = (
            f"🖥 Модуль: <b>{module.name}</b>\n" + (
                f"👨🏿‍💻 Автор: <b>{module.author}</b>\n" if module.author else ""
            ) + (
                f"🔢 Версия: <b>{module.version}</b>\n" if module.version else ""
            ) + (
                f"\n📄 Описание:\n"
                f"    ╰ {module.__doc__ or 'Нет описания для модуля'}\n\n"
            )
        )

        return await utils.answer(
            message, header + command_descriptions + "\n" + inline_descriptions
        )
