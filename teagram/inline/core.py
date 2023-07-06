from pyrogram import Client
from .. import db

_db = db.load_db()

client = Client(
    name='Teagram',
    api_id = _db['api_id'],
    api_hash = _db['api_hash'],
    bot_token = _db['token']
)