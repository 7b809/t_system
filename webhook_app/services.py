import os
from .utils import parse_alert_message
from order_engine.engine import should_place_order
from order_engine.orders import place_order


# 🔹 BASIC LOG FLAG (single source of truth)
BASIC_LOGS = os.getenv("BASIC_LOGS", "false").lower() == "true"


def process_alert(data):
    """
    Main logic layer:
    """

    try:
        # -----------------------------
        # 📩 Step 1: Extract inputs
        # -----------------------------
        raw_message = data.get("message", "")
        security_id = data.get("security_id")
        mode = data.get("mode", "PAPER").upper()

        # ✅ force_order flag
        force_order = data.get("force_order", False)

        # 🔹 Conditional logs
        if BASIC_LOGS:
            print("📩 Incoming Message:", raw_message)
            print("📌 Security ID:", security_id)
            print("⚙️ Mode:", mode)
            print("⚡ Force Order:", force_order)

        # -----------------------------
        # ❌ Validation
        # -----------------------------
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

        # -----------------------------
        # 🧾 Step 2: Parse message
        # -----------------------------
        parsed = parse_alert_message(raw_message)

        if not parsed:
            return {
                "status": "error",
                "reason": "Parsing failed"
            }

        # -----------------------------
        # ✅ Step 3: Attach required fields
        # -----------------------------
        parsed["security_id"] = str(security_id)
        parsed["mode"] = mode
        parsed["force_order"] = force_order

        if BASIC_LOGS:
            print("✅ Parsed Data:", parsed)

        # -----------------------------
        # 🎯 Step 4: Identify signal type
        # -----------------------------
        signal_type = parsed.get("type")

        if signal_type == "buyCE":
            action = "CALL BUY SIGNAL"
        elif signal_type == "buyPE":
            action = "PUT BUY SIGNAL"
        else:
            action = "UNKNOWN"

        # -----------------------------
        # ⚙️ Step 5: Engine decision
        # -----------------------------
        should_execute, result = should_place_order(parsed)

        if should_execute:

            # -----------------------------
            # 🚀 Step 6: Place order
            # -----------------------------
            order = place_order(parsed, result)

            # 🛑 Handle duplicate / ignored case
            if isinstance(order, dict) and order.get("status") == "ignored":
                return {
                    "status": "success",
                    "action": action,
                    "execution": "IGNORED",
                    "mode": mode,
                    "reason": order.get("reason"),
                    "existing_order": order.get("existing_order")
                }

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
        # 🔥 ALWAYS print errors (not controlled by BASIC_LOGS)
        print("❌ ERROR in process_alert:", str(e))

        return {
            "status": "error",
            "reason": str(e)
        }