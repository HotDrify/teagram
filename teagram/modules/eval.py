import logging
import ast

from pyrogram import Client, types
from .. import loader, utils


def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)

            
async def execute_python_code(code, env: dict = {}):
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
    

@loader.module(name="Eval")
class EvalMod(loader.Module):
    """Используйте eval прямо через 🍵teagram!"""
    async def ecmd(self, app: Client, message: types.Message, args: str):
        
        result = await execute_python_code(
            args,
            # Env
            {
                'client': app,
                'message': message, 
                'args': args
            }
        )
        await utils.answer(
            message,
            f"""
```
🍵 Teagram | UserBot
Code 💻:
{args}
Output 💻:
{result}
```
"""
        )
