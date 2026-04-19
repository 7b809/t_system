import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

_client = None
_collection = None


def get_orders_collection():
    global _client, _collection

    if _collection is None:
        _client = MongoClient(MONGO_URI)
        db = _client["trading"]
        _collection = db["orders"]

        print("✅ Mongo Orders Connected")

    return _collection