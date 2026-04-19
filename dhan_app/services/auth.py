import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "trading"
COLLECTION_NAME = "auth"

_client = None
_collection = None


def get_collection():
    global _client, _collection

    if _collection is None:
        if not MONGO_URI:
            raise ValueError("❌ MONGO_URI not found")

        _client = MongoClient(MONGO_URI)
        db = _client[DB_NAME]
        _collection = db[COLLECTION_NAME]

        print("✅ MongoDB connected")

    return _collection


def load_valid_dhan_credentials():
    try:
        collection = get_collection()

        data = collection.find_one({"_id": "dhan_token"})

        if not data:
            print("❌ No token found")
            return None

        data.pop("_id", None)

        client_id = data.get("dhanClientId")
        token = data.get("accessToken")
        expiry = data.get("expiryTime")

        if not client_id or not token or not expiry:
            print("❌ Missing fields")
            return None

        expiry_dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))

        if datetime.now(timezone.utc) >= expiry_dt:
            print("❌ Token expired")
            return None

        return {
            "client_id": client_id,
            "access_token": token
        }

    except Exception as e:
        print("❌ Auth error:", e)
        return None