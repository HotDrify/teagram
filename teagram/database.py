"""
тут находится бд

    """

import json

def save_db(api_id: int, hash_id: str, token: str, prefix: str = '.', modules: dict = None):
    """_summary_

    Args:
        api_id (int): _description_
        hash_id (str): _description_
        token (str): _description_
        prefix (str, optional): _description_. Defaults to '.'.
        modules (dict, optional): _description_. Defaults to None.
    """
    data = {
        'api_id': api_id,
        'hash_id': hash_id,
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