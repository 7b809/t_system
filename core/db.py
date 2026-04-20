from pymongo import MongoClient
import os

_auth_client = None
_order_client = None


# -----------------------------------
# 🔐 AUTH DB CLIENT
# -----------------------------------
def get_auth_mongo_client():
    global _auth_client

    if _auth_client is None:
        uri = os.getenv("AUTH_MONGO_URI")

        if not uri:
            raise ValueError("❌ AUTH_MONGO_URI missing")

        _auth_client = MongoClient(uri)

        print("✅ Auth Mongo Connected")

    return _auth_client


# -----------------------------------
# 📦 ORDER DB CLIENT
# -----------------------------------
def get_order_mongo_client():
    global _order_client

    if _order_client is None:
        uri = os.getenv("AUTH_MONGO_URI")

        if not uri:
            raise ValueError("❌ ORDER_MONGO_URI missing")

        _order_client = MongoClient(uri)

        print("✅ Order Mongo Connected")

    return _order_client