from datetime import datetime, timezone
import os
from dotenv import load_dotenv

from core.db import get_auth_mongo_client   # ✅ FIXED

load_dotenv()

# -----------------------------------
# 🔧 CONFIG FROM ENV
# -----------------------------------
DB_NAME = os.getenv("AUTH_DB_NAME", "dhan_system")
COLLECTION_NAME = os.getenv("AUTH_COLLECTION_NAME", "access_tokens")

_collection = None


# -----------------------------------
# 📦 GET COLLECTION
# -----------------------------------
def get_collection():
    global _collection

    if _collection is None:
        client = get_auth_mongo_client()   # ✅ FIXED

        if client is None:
            raise ValueError("❌ Auth Mongo client not initialized")

        db = client[DB_NAME]
        _collection = db[COLLECTION_NAME]

        print(f"✅ Auth Mongo Connected → DB: {DB_NAME}, Collection: {COLLECTION_NAME}")

    return _collection


# -----------------------------------
# 🔐 LOAD VALID DHAN CREDENTIALS
# -----------------------------------
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

        # ✅ Fix timezone safely
        if expiry.endswith("Z"):
            expiry = expiry.replace("Z", "+00:00")

        expiry_dt = datetime.fromisoformat(expiry)

        if expiry_dt.tzinfo is None:
            expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)

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