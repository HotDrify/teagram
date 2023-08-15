import sys
import asyncio
import subprocess

from getpass import types # type: ignore
from .. import loader, utils

async def execute_python_code(code, env={}):
    # sourcery skip: inline-immediately-returned-variable
    try:
        fn_name = "_eval_expr"
        cmd = "\n".join(f" {i}" for i in code.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        
        p = subprocess.Popen(['python', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = p.communicate(body)
        
        if stderr:
            return stderr
        
        env = {'import': __import__, **env}
        exec(compile(stdout, filename="<ast>", mode="exec"), env)
        result = await eval(f"{fn_name}()", env)
        
        return result
    except Exception as error:
        return error

@loader.module(name="Eval", author='teagram')
class EvalMod(loader.Module):
    """Используйте eval прямо через 🍵teagram!"""
        
    """test"""
    async def e_cmd(self, app: Client, message: types.Message, args: str): # type: ignore
        result = await execute_python_code(
            args,
            {
                'self': self,
                'client': app,
                'app': app,
                'message': message,
                'args': args
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
