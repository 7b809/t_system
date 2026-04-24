import uuid
from datetime import datetime

from order_engine.db import get_orders_collection
from dhan_app.services.orders import place_order as dhan_place_order


# -----------------------------------
# 🎯 CLEAN TRADE LOG FORMATTER
# -----------------------------------
def print_trade_log(order, action="EXECUTED"):
    print("\n==============================")

    if order.get("mode") == "PAPER":
        print(f"🧪 PAPER TRADE {action}")
    else:
        print(f"🚀 LIVE TRADE {action}")

    print("==============================")

    print(f"Index      : {order.get('index_id')}")
    print(f"Signal     : {order.get('type')}")
    print(f"Strike     : {order.get('strike')}")
    print(f"Option ID  : {order.get('security_id')}")
    print(f"Entry      : {order.get('executed_price')}")
    print(f"Index LTP  : {order.get('index_ltp')}")
    print(f"Time       : {order.get('timestamp')}")

    print("==============================\n")


# -----------------------------------
# 🔍 GET LAST ACTIVE ORDER
# -----------------------------------
def get_last_order(index_id):
    collection = get_orders_collection()

    return collection.find_one(
        {
            "index_id": str(index_id),
            "status": {"$in": ["EXECUTED", "LIVE_EXECUTED"]}
        },
        sort=[("timestamp", -1)]
    )


# -----------------------------------
# ❌ EXIT ORDER
# -----------------------------------
def exit_order(existing_order):
    collection = get_orders_collection()

    print("\n==============================")
    print("❌ POSITION EXITED")
    print("==============================")
    print(f"Index      : {existing_order.get('index_id')}")
    print(f"Signal     : {existing_order.get('type')}")
    print(f"Exit Time  : {datetime.utcnow().isoformat()}")
    print("==============================\n")

    update_data = {
        "status": "EXITED",
        "exit_time": datetime.utcnow().isoformat()
    }

    collection.update_one(
        {"_id": existing_order["_id"]},
        {"$set": update_data}
    )

    existing_order.update(update_data)

    return existing_order


# -----------------------------------
# 🚀 PLACE ORDER
# -----------------------------------
def place_order(alert, market_data):
    """
    Handles BOTH:
    - PAPER trades
    - LIVE trades
    + POSITION REVERSAL LOGIC
    """

    mode = alert.get("mode", "PAPER").upper()

    new_type = alert.get("type")

    # 🔥 FIX: use INDEX ID instead of option contract id
    index_id = str(alert.get("security_id"))

    # (keep option id separately)
    option_sec_id = str(market_data.get("sec_id"))

    # -----------------------------------
    # 🔁 CHECK EXISTING POSITION
    # -----------------------------------
    last_order = get_last_order(index_id)

    if last_order:
        last_type = last_order.get("type")

        # 🔁 REVERSAL
        if last_type != new_type:
            print(f"🔁 Reversal detected: {last_type} → {new_type}")
            exit_order(last_order)
 
        # 🛑 SAME SIDE
        elif last_type == new_type:
            print("⚠️ Same position already active → logging as IGNORED")

            ignored_order = {
                "order_id": str(uuid.uuid4()),
                "type": new_type,
                "alert_price": float(alert.get('price')),
                "executed_price": float(market_data.get('ltp')),

                "index_id": index_id,
                "security_id": option_sec_id,

                "index_ltp": market_data.get("index_ltp"),
                "strike": market_data.get("strike"),
                "timestamp": datetime.utcnow().isoformat(),

                "mode": mode,
                "status": "IGNORED",  # ✅ NEW
                "reason": "Same position already active"
            }

            saved_order = save_order(ignored_order)

            print_trade_log(saved_order, action="IGNORED")

            return {
                "status": "ignored",
                "reason": "Same position already active",
                "order": saved_order
            }

    # -----------------------------------
    # 🔥 BASE ORDER STRUCTURE
    # -----------------------------------
    base_order = {
        "order_id": str(uuid.uuid4()),
        "type": new_type,
        "alert_price": float(alert.get('price')),
        "executed_price": float(market_data.get('ltp')),

        "index_id": index_id,
        "security_id": option_sec_id,

        "index_ltp": market_data.get("index_ltp"),
        "strike": market_data.get("strike"),
        "timestamp": datetime.utcnow().isoformat(),
        "mode": mode
    }

    # -----------------------------------
    # 🧪 PAPER TRADE
    # -----------------------------------
    if mode == "PAPER":
        base_order["status"] = "EXECUTED"

        saved_order = save_order(base_order)

        # ✅ CLEAN LOG
        print_trade_log(saved_order)

        return saved_order

    # -----------------------------------
    # 🚀 LIVE TRADE
    # -----------------------------------
    elif mode == "LIVE":
        try:
            response = dhan_place_order(
                security_id=market_data["sec_id"],
                price=market_data["ltp"]
            )

            if isinstance(response, dict) and response.get("status") == "success":
                base_order["status"] = "LIVE_EXECUTED"
            else:
                base_order["status"] = "LIVE_FAILED"

            base_order["broker_response"] = response

        except Exception as e:
            base_order["status"] = "LIVE_FAILED"
            base_order["error"] = str(e)

        saved_order = save_order(base_order)

        # ✅ CLEAN LOG
        print_trade_log(saved_order, action=saved_order.get("status"))

        return saved_order

    # -----------------------------------
    # ❌ INVALID MODE
    # -----------------------------------
    else:
        return {
            "status": "error",
            "msg": f"Invalid mode: {mode}"
        }


# -----------------------------------
# 💾 SAVE ORDER
# -----------------------------------
def save_order(order):
    try:
        collection = get_orders_collection()

        db_order = order.copy()

        result = collection.insert_one(db_order)

        order["_id"] = str(result.inserted_id)

        return order

    except Exception as e:
        print("❌ Mongo save error:", e)
        return {
            "status": "error",
            "msg": str(e)
        }


# -----------------------------------
# 🔄 SERIALIZE ORDER
# -----------------------------------
def serialize_order(doc):
    doc = dict(doc)

    if "_id" in doc:
        doc["_id"] = str(doc["_id"])

    return doc


# -----------------------------------
# 📊 GET ALL ORDERS
# -----------------------------------
def get_all_orders():
    collection = get_orders_collection()

    orders = list(collection.find())

    return [serialize_order(o) for o in orders]

