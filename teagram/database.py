import json


def save_db(
        api_id: int, api_hash: str, token: str = None, prefix: str = '.',
        modules: dict = None):
    """Save database to a JSON file.

    Args:
        api_id (int): The API ID.
        api_hash (str): The hash ID.
        token (str, optional): The token. Defaults to None.
        prefix (str, optional): The prefix. Defaults to '.'.
        modules (dict, optional): The modules. Defaults to None.
    """
    data = {
        'api_id': api_id,
        'api_hash': api_hash,
        'token': token,
        'prefix': prefix,
        'modules': modules
    }

    try:
        with open('./inline/config.json', 'w') as file:
            json.dump(data, file, indent=4)
    except Exception:
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
    except Exception:
        with open('./inline/config.json', 'r') as file:
            data = file.read()

    if not data:
        api_id = None
        api_hash = None

        def register():
            try:
                global api_id, api_hash
                
                api_id = int(input('Введите api_id: ').strip())
                if len(api_id) != 8:
                    raise ValueError()
                
                api_hash = input('Введите api_hash: ').strip()

            except ValueError:
                print('Неправильный api_id или api_hash')

                register()

        register()

        data = {
            'api_id': api_id,
            'api_hash': api_hash,
            'token': None,
            'prefix': '.',
            'modules': None
        }

        save_db(api_id, api_hash)
    else:
        data = json.loads(data)

    return data
