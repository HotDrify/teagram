"""Данный модуль выбирает лучший JSON-модуль из доступных и обеспечивает совместимость"""
from typing import Callable

try:
    import rapidjson as json
except ImportError:
    try:
        import ujson as json
    except ImportError:
        try:
            import simplejson as json
        except ImportError:
            import json

_jname: str = json.__name__.lower().strip()
if _jname != "ujson":
    import json as _json


class JSONDecoder:
    def __init__(self) -> None:
        if _jname == "ujson":
            decode: Callable = json.decode
        else:
            self.decode: Callable = _json.JSONDecoder().decode


class JSONEncoder:
    def __init__(self) -> None:
        if _jname == "ujson":
            self.encode: Callable = json.encode
        else:
            self.encode: Callable = _json.JSONEncoder().encode


json.JSONEncoder = JSONEncoder
json.JSONDecoder = JSONDecoder
