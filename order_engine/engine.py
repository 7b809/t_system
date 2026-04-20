from ws_feed.price_store import get_price
import os
from option_selector.services import get_option_contract


# 🔥 Proper boolean parsing from env
THRESHOLD_CHECK = os.getenv("THRESHOLD_CHECK", "false").lower() == "true"

RANGE = 10  # used only if threshold_check = True


def should_place_order(alert):
    try:
        # -----------------------------
        # ✅ VALIDATION
        # -----------------------------
        if 'price' not in alert:
            return False, "Missing price in alert"

        if 'security_id' not in alert:
            return False, "Missing security_id"

        if 'type' not in alert:
            return False, "Missing type (buyCE/buyPE)"

        alert_price = float(alert['price'])
        index_sec_id = str(alert['security_id'])
        option_type = alert.get("type")

        # -----------------------------
        # 📡 STEP 1: GET INDEX LTP
        # -----------------------------
        live_data = get_price(index_sec_id)

        if not live_data:
            return False, f"No live data for security_id={index_sec_id}"

        ltp_raw = live_data.get("LTP")

        if ltp_raw is None:
            return False, f"LTP missing in feed for {index_sec_id}"

        index_ltp = float(ltp_raw)

        diff = abs(index_ltp - alert_price)

        print(f"📊 Compare | Sec: {index_sec_id} | Alert: {alert_price} | LTP: {index_ltp} | Diff: {diff}")

        # -----------------------------
        # 🔥 CASE 1: NO THRESHOLD CHECK
        # -----------------------------
        if not THRESHOLD_CHECK:
            print("🚀 Threshold check DISABLED → MARKET EXECUTION")

            option_data = get_option_contract(
                security_id=index_sec_id,
                option_type=option_type
            )

            if "error" in option_data:
                return False, option_data["error"]

            return True, {
                "sec_id": str(option_data["security_id"]),   # ✅ OPTION CONTRACT ID
                "ltp": float(option_data["price"]),          # ✅ OPTION PRICE
                "alert_price": alert_price,
                "index_ltp": index_ltp,
                "mode": "MARKET_EXECUTION",
                "strike": option_data.get("strike")
            }

        # -----------------------------
        # 🔥 CASE 2: WITH THRESHOLD
        # -----------------------------
        if diff <= RANGE:
            print("✅ Within threshold → selecting option contract")

            option_data = get_option_contract(
                security_id=index_sec_id,
                option_type=option_type
            )

            if "error" in option_data:
                return False, option_data["error"]

            return True, {
                "sec_id": str(option_data["security_id"]),
                "ltp": float(option_data["price"]),
                "alert_price": alert_price,
                "index_ltp": index_ltp,
                "diff": diff,
                "strike": option_data.get("strike")
            }

        # -----------------------------
        # ❌ OUT OF RANGE
        # -----------------------------
        return False, f"Out of range (Index LTP={index_ltp}, Alert={alert_price}, Diff={diff})"

    except Exception as e:
        return False, f"Engine error: {str(e)}"