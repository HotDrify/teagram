import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps as _wraps
from inspect import iscoroutinefunction
from types import ModuleType
from typing import Callable


def wrap_function_to_async(function: Callable) -> Callable:
    """
    Оборачивает синхронные функции в асинхронные
    """
    assert (not iscoroutinefunction(function)), "Функция уже асинхронная!"

    pool = ThreadPoolExecutor()

    @_wraps(function)
    def wrapped(*args, **kwargs):

        future = pool.submit(function, *args, **kwargs)
        return asyncio.wrap_future(future)

    return wrapped


class WrapModuleToAsync:
    """
    Делает то же самое что и wrap_to_async_function, но оборачивает уже целые модули
    """

    def __init__(self, mod: ModuleType):
        for attr in dir(mod):
            item = getattr(mod, attr)
            if callable(item) and not iscoroutinefunction(item):
                wrapped = wrap_function_to_async(item)
                setattr(self, attr, wrapped)
