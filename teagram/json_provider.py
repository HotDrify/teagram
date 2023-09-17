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

if _jname != "json":
    import json as _json
    json_attr = dir(json)
    missing = dir(_json)
    for i in json_attr:
        if i in missing:
            missing.remove(i)
        
    for item in missing:
        json_item = getattr(_json, item)
        setattr(json, item, json_item)