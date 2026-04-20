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

    # -------------------------
    # 🔥 BASE ORDER STRUCTURE
    # -------------------------
    base_order = {
        "order_id": str(uuid.uuid4()),
        "type": alert.get('type'),
        "alert_price": float(alert.get('price')),
        "executed_price": float(market_data.get('ltp')),
        "security_id": str(market_data.get('sec_id')),   # ✅ OPTION CONTRACT ID
        "index_ltp": market_data.get("index_ltp"),       # ✅ underlying index price
        "strike": market_data.get("strike"),             # ✅ strike price
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
        try:
            response = dhan_place_order(
                security_id=market_data["sec_id"],
                price=market_data["ltp"]   # 🔥 market execution
            )

            base_order["status"] = "LIVE_EXECUTED"
            base_order["broker_response"] = response

        except Exception as e:
            base_order["status"] = "LIVE_FAILED"
            base_order["error"] = str(e)

        saved_order = save_order(base_order)

        print("🚀 LIVE ORDER:", saved_order)

        return saved_order

    # -------------------------
    # ❌ INVALID MODE
    # -------------------------
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

        # 🔥 copy to avoid mutation issues
        db_order = order.copy()

        result = collection.insert_one(db_order)

        # ✅ attach string _id
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
    doc = dict(doc)

    if "_id" in doc:
        doc["_id"] = str(doc["_id"])

    return doc


def get_all_orders():
    collection = get_orders_collection()

    orders = list(collection.find())

    return [serialize_order(o) for o in orders]