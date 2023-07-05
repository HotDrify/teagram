import json


def save_db(api_id: int, hash_id: str, token: str = None, prefix: str = '.', modules: dict = None):
    """Save database to a JSON file.

    Args:
        api_id (int): The API ID.
        hash_id (str): The hash ID.
        token (str, optional): The token. Defaults to None.
        prefix (str, optional): The prefix. Defaults to '.'.
        modules (dict, optional): The modules. Defaults to None.
    """
    data = {
        'api_id': api_id,
        'hash_id': hash_id,
        'token': token,
        'prefix': prefix,
        'modules': modules
    }

    try:
        with open('./inline/config.json', 'w') as file:
            json.dump(data, file, indent=4)
    except:
        with open('./teagram/inline/config.json', 'w') as file:
            json.dump(data, file, indent=4)


def load_db():
    """Load database from a JSON file.

    Returns:
        dict: The loaded database data.
    """
    try:
        with open('./teagram/inline/config.json', 'r') as file:
            data = file.read()
    except:
        with open('./inline/config.json', 'r') as file:
            data = file.read()

    if not data:
        data = {
            'api_id': None,
            'api_hash': None,
            'token': None,
            'prefix': '.',
            'modules': None
        }    
    else:
        data = json.loads(data)

    return data
