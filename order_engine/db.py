import os
from core.db import get_order_mongo_client   # ✅ correct client
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------
# 🔧 CONFIG FROM ENV
# -----------------------------------
DB_NAME = os.getenv("ORDER_DB_NAME", "trading")
COLLECTION_NAME = os.getenv("ORDER_COLLECTION_NAME", "orders")

_collection = None


# -----------------------------------
# 📦 GET ORDERS COLLECTION
# -----------------------------------
def get_orders_collection():
    global _collection

    if _collection is None:
        client = get_order_mongo_client()   # ✅ FIXED

        if client is None:
            raise ValueError("❌ Order Mongo client not initialized")

        db = client[DB_NAME]
        _collection = db[COLLECTION_NAME]

        print(f"✅ Mongo Orders Connected → DB: {DB_NAME}, Collection: {COLLECTION_NAME}")

    return _collection