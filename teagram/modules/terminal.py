from subprocess import check_output
from telethon import TelegramClient, types

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
    async def terminal_cmd(self, message: types.Message, args: str):
        message = message.chat.id
        await self._client.send_message(message, "☕")
        output = await bash_exec(args)

        await self._client.send_message(
            message,
            f"""
<emoji id=5472111548572900003>⌨️</emoji> <b>Команда:</b> <code>{args.strip()}</code>
💾 <b>Вывод:</b><code>
{output}
</code>
""", parse_mode='html')
