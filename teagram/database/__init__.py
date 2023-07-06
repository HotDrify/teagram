__all__ = ["CloudDatabase", "Database"]

from .backend import CloudDatabase
from .frontend import Database

db = Database("./db.json")
