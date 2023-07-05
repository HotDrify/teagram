import json

def save_db(token: str, prefix: str = '.', modules: dict = None):
    data = {
        'token': token,
        'prefix': prefix,
        'modules': modules
    }

    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_db():
    with open('config.json', 'r') as file:
        data = json.loads(file.read())

    return data

