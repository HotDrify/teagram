import logging
from subprocess import check_output

from pyrogram import Client, types

from .. import loader, utils


@loader.module(name="Terminal")
class TerminalMod(loader.Module):
    """Используйте терминал BASH прямо через 🍵teagram!"""
    async def terminal_cmd(self, app: Client, message: types.Message, args: str):
        await utils.answer(message, "☕")
        try:
            output = check_output(args.strip(), shell=True).decode()
        except Exception as error:
            output = error
        await utils.answer(
            message,
            f"""
<code>🍵 teagram | UserBot</code>
📥 <b>input</b>:
<code>{args}</code>
📤 <b>output</b>:
<code>{output}</code>
```
        """
        )
