import ast

from .. import loader, utils
from pyrogram import Client, types

import subprocess
import tempfile
import os

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
        result = (await eval(f"{fn_name}()", env))
        
        return result
    except Exception as error:
        return error

@loader.module(name="Evalutor", author='teagram')
class EvalutorMod(loader.Module):
    """Используйте eval разных языков прямо через 🍵teagram!"""

    async def e_cmd(self, app: Client, message: types.Message, args: str): # type: ignore
        result = await execute_python_code(
            args,
            {
                'self': self,
                'client': app,
                'app': app,
                'message': message,
                'args': args,
                'reply': message.reply_to_message,
                'db': self.db,
                'chat': message.chat,
                'm': message,
                'a': app,
                'r': message.reply_to_message,
                'manager': self.all_modules,
                'bot': self.bot,
                'pyrogram': __import__('pyrogram'),
                'os': __import__('os')
            }
        )
        await utils.answer(
            message,
            f"""
<b>💻 Code</b>:
<code>{args}</code>

<b>💻 Output</b>:
<code>{result}</code>
    """
        )
    async def ecpp_cmd(self, app: Client, message: types.Message, args: str): #type: ingnore
        try:
            subprocess.check_output(
                ["gcc", "g++", "--version"],
                stderr=subprocess.STDOUT,
            )
        except Exception:
            return await utils.answer(
                message,
                "🚫 произошла ошибка! проверьте наличие <code>gcc</code> команды на вашем сервере."
            )
        await utils.answer(
            message,
            "⏳ идет компиляция кола...")
        with tempfile.TemporaryDirectory() as tempdir: # https://github.com/hikariatama/Hikka/blob/ce1f24f03313f8500de671815dde065fc8d86897/hikka/modules/eval.py#L213
            file = os.path.join(tmpdir, "code.cpp")
            with open(file, "w") as f:
                f.write(args)
            result = subprocess.check_output(
                ["gcc", "g++", "-o", "code", "code.cpp"],
                cwd=tempdir,
                stderr=subprocess.STDOUT,
            ).decode()
            await utils.answer(
                message,
                f"""
                <b>💻 cpp code</b>:
                <code>{args}</code>

                <b>💻 Output</b>:
                <code>{result}</code>
                """)
                
