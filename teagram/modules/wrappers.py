import inspect
from types import ModuleType
from typing import Callable


def wrap_to_async_function(function: Callable) -> Callable:
    """
    Делает из обычной функции асинхронную функцию
    """
    assert (inspect.iscoroutinefunction(function)), "Функция уже асинхронная!"

    async def async_function(*args, **kwargs):
        function()
    return async_function


class WrapModuleToAsync:
    """
    Делает то же самое что и wrap_to_async_function, но оборачивает уже целые модули
    """

    def __init__(self, mod: ModuleType):
        for attr in dir(mod):
            item = getattr(mod, attr)
            if callable(item) and not inspect.iscoroutinefunction(item):
                wrapped = wrap_to_async_function(item)
                setattr(self, attr, wrapped)
