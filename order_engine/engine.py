from ws_feed.price_store import get_price
import os
THRESHOLD_CHECK = os.getenv("THRESHOLD_CHECK")   # 🔥 disable range logic

RANGE = 10  # used only if threshold_check = True


def should_place_order(alert):
    try:
        if 'price' not in alert:
            return False, "Missing price in alert"

        if 'security_id' not in alert:
            return False, "Missing security_id"

        alert_price = float(alert['price'])
        sec_id = str(alert['security_id'])

        live_data = get_price(sec_id)

        if not live_data:
            return False, f"No live data for security_id={sec_id}"

        ltp_raw = live_data.get("LTP")

        if ltp_raw is None:
            return False, f"LTP missing in feed for {sec_id}"

        ltp = float(ltp_raw)

        diff = abs(ltp - alert_price)

        print(f"📊 Compare | Sec: {sec_id} | Alert: {alert_price} | LTP: {ltp} | Diff: {diff}")

        # 🔥 CASE 1: NO THRESHOLD → ALWAYS EXECUTE
        if not THRESHOLD_CHECK:
            return True, {
                "sec_id": sec_id,
                "ltp": ltp,
                "alert_price": alert_price,
                "diff": diff,
                "mode": "MARKET_EXECUTION"
            }

        # 🔥 CASE 2: WITH THRESHOLD
        if diff <= RANGE:
            return True, {
                "sec_id": sec_id,
                "ltp": ltp,
                "alert_price": alert_price,
                "diff": diff
            }

        return False, f"Out of range (LTP={ltp}, Alert={alert_price}, Diff={diff})"

    except Exception as e:
        return False, f"Engine error: {str(e)}"