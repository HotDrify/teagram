import logging
from subprocess import check_output

from pyrogram import Client, types

from .. import loader, utils
from ..wrappers import wrap_function_to_async

@wrap_function_to_async
def bash_exec(args: str):
    try:
        output = check_output(args.strip(), shell=True)
        output = output.decode()

        return output
    except UnicodeDecodeError:
        return check_output(args.strip(), shell=True)
    except Exception as error:
        return error


@loader.module(name="Terminal", author='teagram')
class TerminalMod(loader.Module):
    """Используйте терминал BASH прямо через 🍵teagram!"""
    async def bash_cmd(self, app: Client, message: types.Message, args: str):
        await utils.answer(message, "☕")
        output = await bash_exec(args)

        await utils.answer(
            message,
            f"""
<code>🍵 teagram | UserBot</code>
📥 <b>input</b>:
<code>{args.strip()}</code>
📤 <b>output</b>:
<code>{output}</code>
```
        """
        )
