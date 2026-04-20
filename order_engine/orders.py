import uuid
from datetime import datetime

from order_engine.db import get_orders_collection
from dhan_app.services.orders import place_order as dhan_place_order


def place_order(alert, market_data):
    """
    Handles BOTH:
    - PAPER trades
    - LIVE trades
    """

    mode = alert.get("mode", "PAPER").upper()

    base_order = {
        "order_id": str(uuid.uuid4()),
        "type": alert['type'],
        "alert_price": float(alert['price']),
        "executed_price": market_data['ltp'],
        "security_id": market_data['sec_id'],
        "timestamp": datetime.utcnow().isoformat(),
        "mode": mode
    }

    # -------------------------
    # 🧪 PAPER TRADE
    # -------------------------
    if mode == "PAPER":
        base_order["status"] = "EXECUTED"

        saved_order = save_order(base_order)

        print("🧪 PAPER ORDER:", saved_order)

        return saved_order

    # -------------------------
    # 🚀 LIVE TRADE
    # -------------------------
    elif mode == "LIVE":

        response = dhan_place_order(
            security_id=market_data["sec_id"],
            price=market_data["ltp"]
        )

        base_order["status"] = "LIVE_EXECUTED"
        base_order["broker_response"] = response

        saved_order = save_order(base_order)

        print("🚀 LIVE ORDER:", saved_order)

        return saved_order

    else:
        return {
            "status": "error",
            "msg": f"Invalid mode: {mode}"
        }


def save_order(order):
    """
    Save order in Mongo and return JSON-safe order
    """
    try:
        collection = get_orders_collection()

        result = collection.insert_one(order)

        # ✅ Add _id as string (IMPORTANT FIX)
        order["_id"] = str(result.inserted_id)

        return order

    except Exception as e:
        print("❌ Mongo save error:", e)
        return {
            "status": "error",
            "msg": str(e)
        }


def serialize_order(doc):
    """
    Convert Mongo document to JSON-safe format
    """
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def get_all_orders():
    collection = get_orders_collection()

    orders = list(collection.find())

    # ✅ Convert all ObjectId → string
    return [serialize_order(o) for o in orders]