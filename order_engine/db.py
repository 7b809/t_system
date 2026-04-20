from core.db import get_mongo_client   # ✅ shared Mongo client

DB_NAME = "trading"
COLLECTION_NAME = "orders"

_collection = None


def get_orders_collection():
    global _collection

    if _collection is None:
        client = get_mongo_client()   # ✅ reuse global client

        if client is None:
            raise ValueError("❌ Mongo client not initialized")

        db = client[DB_NAME]
        _collection = db[COLLECTION_NAME]

        print("✅ Mongo Orders Connected")

    return _collection