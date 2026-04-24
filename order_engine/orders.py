import uuid
from datetime import datetime

from order_engine.db import get_orders_collection
from dhan_app.services.orders import place_order as dhan_place_order

import threading,time

order_lock = threading.Lock()

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
# 🔥 NEW: TRAILING LOGIC (ADDED)
# -----------------------------------
def update_trailing(order, current_price):
    try:
        entry = float(order.get("executed_price", 0))
        sl = float(order.get("sl", entry - 10))
        step = float(order.get("trail_step", 5))

        highest = float(order.get("highest_price", entry))

        if current_price > highest:
            highest = current_price

        # move SL to breakeven
        if current_price >= entry + step:
            sl = max(sl, entry)

        # trailing move
        new_sl = current_price - step
        if new_sl > sl:
            sl = new_sl

        order["sl"] = sl
        order["highest_price"] = highest

        return order

    except Exception as e:
        print("❌ Trailing error:", e)
        return order


# -----------------------------------
# 🔥 NEW: EXIT CHECK (ADDED)
# -----------------------------------
def should_exit(order, current_price):
    try:
        entry = float(order.get("executed_price", 0))
        sl = float(order.get("sl", entry - 10))

        # SL HIT
        if current_price <= sl:
            return True, "SL HIT"

        # TARGET HIT (10 points)
        if current_price >= entry + 10:
            return True, "TARGET HIT"

        return False, None

    except Exception as e:
        print("❌ Exit check error:", e)
        return False, None


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


def exit_order(existing_order, market_data):
    try:
        collection = get_orders_collection()

        print("\n==============================")
        print("❌ POSITION EXITED")
        print("==============================")
        print(f"Index      : {existing_order.get('index_id')}")
        print(f"Signal     : {existing_order.get('type')}")
        print(f"Exit Time  : {datetime.utcnow().isoformat()}")
        print("==============================\n")

        entry_price = float(existing_order.get("executed_price", 0))
        exit_price = float(market_data.get("ltp", entry_price))

        if existing_order.get("type") == "buyCE":
            pnl = exit_price - entry_price
        else:
            pnl = entry_price - exit_price

        update_data = {
            "status": "EXITED",
            "exit_time": datetime.utcnow().isoformat(),
            "pnl": pnl
        }

        result = collection.update_one(
            {"_id": existing_order["_id"]},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            print("❌ Exit update failed")
            return False

        existing_order.update(update_data)

        return True

    except Exception as e:
        print("❌ Exit failed:", e)
        return False


# -----------------------------------
# 🚀 PLACE ORDER
# -----------------------------------
def place_order(alert, market_data):
    with order_lock:

        mode = alert.get("mode", "PAPER").upper()
        new_type = alert.get("type")

        index_id = str(alert.get("security_id"))
        option_sec_id = str(market_data.get("sec_id"))

        last_order = get_active_order(index_id)

        if last_order:
            last_type = last_order.get("type")

            if last_type != new_type:
                print(f"🔁 Reversal detected: {last_type} → {new_type}")

                exit_result = exit_order(last_order, market_data)

                if not exit_result:
                    return {
                        "status": "error",
                        "msg": "Exit failed, skipping new entry"
                    }

                time.sleep(1)

            elif last_type == new_type:
                print("⚠️ Same position already active → logging as IGNORED")

                ignored_order = {
                    "order_id": str(uuid.uuid4()),
                    "type": new_type,
                    "alert_price": float(alert.get('price')),
                    "executed_price": None,

                    "index_id": index_id,
                    "security_id": option_sec_id,

                    "index_ltp": market_data.get("index_ltp"),
                    "strike": market_data.get("strike"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": mode,

                    "status": "IGNORED",
                    "pnl": None,
                    "reason": "Duplicate signal"
                }

                return save_order(ignored_order)

        active_check = get_active_order(index_id)

        if active_check:
            if active_check.get("type") == new_type:
                print("🚫 Blocked duplicate (final check)")

                ignored_order = {
                    "order_id": str(uuid.uuid4()),
                    "type": new_type,
                    "alert_price": float(alert.get('price')),
                    "executed_price": None,

                    "index_id": index_id,
                    "security_id": option_sec_id,

                    "index_ltp": market_data.get("index_ltp"),
                    "strike": market_data.get("strike"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": mode,

                    "status": "IGNORED",
                    "pnl": None,
                    "reason": "Final duplicate protection"
                }

                return save_order(ignored_order)

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
            "mode": mode,
            "pnl": 0,

            # 🔥 NEW FIELDS (ADDED ONLY)
            "sl": float(market_data.get("ltp")) - 10,
            "highest_price": float(market_data.get("ltp")),
            "trail_step": 5,
        }

        if mode == "PAPER":
            base_order["status"] = "EXECUTED"
            saved_order = save_order(base_order)
            print_trade_log(saved_order)
            return saved_order

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
            print_trade_log(saved_order, action=saved_order.get("status"))
            return saved_order

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
        result = collection.insert_one(order.copy())
        order["_id"] = str(result.inserted_id)
        return order

    except Exception as e:
        print("❌ Mongo save error:", e)
        return {
            "status": "error",
            "msg": str(e)
        }


def serialize_order(doc):
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def get_all_orders():
    collection = get_orders_collection()
    orders = list(collection.find())
    return [serialize_order(o) for o in orders]


def get_active_order(index_id):
    collection = get_orders_collection()

    return collection.find_one(
        {
            "index_id": str(index_id),
            "status": {"$in": ["EXECUTED", "LIVE_EXECUTED"]}
        },
        sort=[("timestamp", -1)]
    )