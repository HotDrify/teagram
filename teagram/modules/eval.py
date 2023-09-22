import ast

from .. import loader, utils
from telethon import TelegramClient, types

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)

async def execute_python_code(code, env={}):
    try:
        fn_name = "_eval_expr"
        cmd = "\n".join(f" {i}" for i in code.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        insert_returns(body)
        env = {'__import__': __import__, **env}
        exec(compile(parsed, filename="<ast>", mode="exec"), env)
        return (await eval(f"{fn_name}()", env))
    except Exception as error:
        return error

@loader.module(name="Eval", author='teagram')
class EvalMod(loader.Module):
    """Используйте eval прямо через 🍵teagram!"""

    async def e_cmd(self, message: types.Message, args: str):
        result = await execute_python_code(
            args,
            {
                'self': self,
                'client': self.client,
                'app': self.client,
                'manager': self.manager,
                'bot': self.bot,
                'db': self.db,
                'utils': utils,
                'loader': loader,
                'telethon': __import__('telethon'),
                'message': message,
                'reply': await message.get_reply_message(),
                'args': args
            }
        )
        await utils.answer(
            message,
            "<b>💻 Code</b>:\n"
            f"<code>{args}</code>\n"
            "<b>💻 Output</b>:\n"
            f"<code>{result}</code>"
        )
