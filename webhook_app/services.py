from .utils import parse_alert_message
from order_engine.engine import should_place_order
from order_engine.orders import place_order


def process_alert(data):
    """
    Main logic layer:
    - Parse TradingView alert
    - Attach security_id (from URL)
    - Attach mode (PAPER / LIVE)
    - Validate with live market price
    - Place order (paper or real)
    """

    try:
        # 📩 Step 1: Extract inputs
        raw_message = data.get("message", "")
        security_id = data.get("security_id")
        mode = data.get("mode", "PAPER").upper()   # ✅ NEW

        print("📩 Incoming Message:", raw_message)
        print("📌 Security ID:", security_id)
        print("⚙️ Mode:", mode)

        # ❌ Validation
        if not raw_message:
            return {
                "status": "error",
                "reason": "Empty message"
            }

        if not security_id:
            return {
                "status": "error",
                "reason": "Missing security_id from URL"
            }

        if mode not in ["PAPER", "LIVE"]:
            return {
                "status": "error",
                "reason": f"Invalid mode: {mode}"
            }

        # 🧾 Step 2: Parse message
        parsed = parse_alert_message(raw_message)

        if not parsed:
            return {
                "status": "error",
                "reason": "Parsing failed"
            }

        # ✅ Step 3: Attach required fields
        parsed["security_id"] = str(security_id)
        parsed["mode"] = mode   # 🔥 IMPORTANT

        print("✅ Parsed Data:", parsed)

        # 🎯 Step 4: Identify signal type
        signal_type = parsed.get("type")

        if signal_type == "buyCE":
            action = "CALL BUY SIGNAL"
        elif signal_type == "buyPE":
            action = "PUT BUY SIGNAL"
        else:
            action = "UNKNOWN"

        # ⚙️ Step 5: Check if order should be placed
        should_execute, result = should_place_order(parsed)

        if should_execute:
            # 🚀 Step 6: Place order (PAPER / LIVE handled inside)
            order = place_order(parsed, result)

            return {
                "status": "success",
                "action": action,
                "execution": "ORDER_PLACED",
                "mode": mode,
                "order": order
            }

        else:
            return {
                "status": "success",
                "action": action,
                "execution": "SKIPPED",
                "mode": mode,
                "reason": result,
                "data": parsed
            }

    except Exception as e:
        print("❌ ERROR in process_alert:", str(e))

        return {
            "status": "error",
            "reason": str(e)
        }