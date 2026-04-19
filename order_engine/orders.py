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

        save_order(base_order)

        print("🧪 PAPER ORDER:", base_order)

        return base_order

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

        save_order(base_order)

        print("🚀 LIVE ORDER:", base_order)

        return base_order

    else:
        return {
            "status": "error",
            "msg": f"Invalid mode: {mode}"
        }


def save_order(order):
    try:
        collection = get_orders_collection()
        collection.insert_one(order)
    except Exception as e:
        print("❌ Mongo save error:", e)


def get_all_orders():
    collection = get_orders_collection()
    return list(collection.find({}, {"_id": 0}))