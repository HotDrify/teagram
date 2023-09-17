import asyncio

from pyrogram import Client, types
from .. import loader, utils

async def bash_exec(command):
    a = await asyncio.create_subprocess_shell(
        command.strip(), 
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    if not (out := await a.stdout.read(-1)):
        try:
            return (await a.stderr.read(-1)).decode()
        except UnicodeDecodeError:
            return f'Unicode decode error: {(await a.stderr.read(-1))}'
    else:
        try:
            return out.decode()
        except UnicodeDecodeError:
            return f'Unicode decode error: {out}'

@loader.module(name="Terminal", author='teagram')
class TerminalMod(loader.Module):
    """Используйте терминал BASH прямо через 🍵teagram!"""
    async def terminal_cmd(self, app: Client, message: types.Message, args: str):
        await utils.answer(message, "☕")
        output = await bash_exec(args)

        await utils.answer(
            message,
            f"""
<emoji id=5472111548572900003>⌨️</emoji> <b>Команда:</b> <code>{args.strip()}</code>
💾 <b>Вывод:</b><code>
{output}
</code>
        """
        )
