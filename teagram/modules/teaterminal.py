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

import asyncio

from telethon import types
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
    strings = {'name': 'terminal'}

    async def terminal_cmd(self, message: types.Message, args: str):
        """Use terminal"""
        await utils.answer(message, "☕")
        
        args = args.strip()
        output = await bash_exec(args)

        await utils.answer(
            message,
            "<emoji document_id=5472111548572900003>⌨️</emoji>"
            f"<b> {self.strings['cmd']}:</b> <code>{args}</code>\n"
            f"💾 <b>{self.strings['output']}:</b>\n<code>"
            f"{output}"
            "</code>"
        )
