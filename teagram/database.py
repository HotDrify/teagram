"""
тут находится бд

    """

import json


def save_db(token: str, prefix: str = '.', modules: dict = None):
    """_summary_

    Args:
        token (str): _description_
        prefix (str, optional): _description_. Defaults to '.'.
        modules (dict, optional): _description_. Defaults to None.
    """
    data = {
        'token': token,
        'prefix': prefix,
        'modules': modules
    }

    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_db():
    """_summary_

    Returns:
        _type_: _description_
    """
    with open('config.json', 'r') as file:
        data = json.loads(file.read())

    return data