from telethon import types
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue

@loader.module(name="Help", author='teagram')
class HelpMod(loader.Module):
    """Помощь по командам 🍵 teagram"""

    strings = {'name': 'help'}
    def __init__(self):
        self.config = Config(
            ConfigValue(
                'smile',
                'smile module_name - commands',
                '⚙',
                self.db.get('Help', 'smile', None),
                validators.String()
            )
        )

    async def help_cmd(self, message: types.Message, args: str):
        """Список всех модулей"""
        try:
            self.bot_username = f'@{(await self.bot.bot.get_me()).username}'
        except:
            self.bot_username = self.strings['ebot']

        if not args:
            text = ""
            for module in sorted(self.manager.modules, key=lambda mod: len(str(mod))):
                if module.name.lower() == 'help':
                    continue

                commands = " <b>|</b> ".join(
                    f"<code>{command}</code>" for command in module.command_handlers
                )

                inline = (
                    " <b>| 🤖</b>: " if module.inline_handlers else ""
                ) + " <b>|</b> ".join(
                    f"<code>{inline_command}</code>"
                    for inline_command in module.inline_handlers
                )
                if commands or inline:
                    text += f"\n{self.config['smile']} <b>{module.name}</b> - " + (commands if commands else self.strings['nocmd']) + inline

            modules_count = len(self.manager.modules) - 1
            bot_inline_info = f"<emoji id=5228968570863496802>🤖</emoji> {self.strings['ibot']}: <b>{self.bot_username}</b>\n"

            return await utils.answer(
                message, 
                f"<emoji id=5359370246190801956>☕️</emoji> {self.strings['mods']} <b>{modules_count}</b>\n{bot_inline_info}{text}"
            )

        module = self.manager.lookup(args)
        if not module:
            return await utils.answer(
                message, f"<b><emoji id=5465665476971471368>❌</emoji> {self.strings['nomod']}</b>")

        prefix = self.db.get("teagram.loader", "prefixes", ["."])[0]

        command_descriptions = "\n".join(
            f"👉 <code>{prefix + command}</code>\n"
            f"    ╰ {(module.command_handlers[command].__doc__ or self.strings['nomd']).strip()}"
            for command in module.command_handlers
        )

        inline_descriptions = "\n".join(
            f"👉 <code>@{f'{self.bot_username} {command}'}</code>\n    ╰ {(module.inline_handlers[command].__doc__ or self.strings['nomd']).strip()}"
            for command in module.inline_handlers
        )

        header = (
            f"<emoji id=5361735750968679136>🖥</emoji> <b>{module.name}</b>\n" +
            (f"<emoji id=5224695503605735506>🧑‍💻</emoji> {self.strings['author']}: <b>{module.author}</b>\n" if module.author else "") +
            (f"<emoji id=5224695503605735506>⌨️</emoji> {self.strings['version']}: <b>{module.version}</b>\n" if module.version else "") +
            (f"\n<emoji id=5400093244895797589>📄</emoji> {self.strings['desc']}:\n    ╰ {module.__doc__ or self.strings['nomd']}\n\n")
        )

        return await utils.answer(
            message, header + command_descriptions + "\n" + inline_descriptions
        )
