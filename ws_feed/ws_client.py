import websocket
import json
import threading
import time

from ws_feed.price_store import update_price
from django.conf import settings


BASE_URL = "wss://sr-webhook.up.railway.app/ws"
SECURITIES = ["13", "21", "51"]

seen_first_tick = {}
prev_price_map = {}


# 🔥 Security ID → Name Mapping
SECURITY_NAME_MAP = {
    "13": "NIFTY",
    "21": "INDIA VIX",
    "51": "SENSEX"
}


def get_config():
    return getattr(settings, "WS_FEED_CONFIG", {})


def log(msg, level="INFO"):
    config = get_config()

    if config.get("TEST_LOG"):
        print(msg)
    elif config.get("SHOW_LTP") and level == "LTP":
        print(msg)


def on_message(ws, message, sec_id):
    try:
        data = json.loads(message)

        # ✅ Always update latest price
        update_price(sec_id, data)

        config = get_config()

        # -----------------------------
        # ✅ FIRST TICK (print once)
        # -----------------------------
        if not seen_first_tick.get(sec_id):
            print(f"✅ [{sec_id}] FIRST DATA RECEIVED")

            if config.get("TEST_LOG"):
                print(f"📥 [{sec_id}] SAMPLE DATA:\n{json.dumps(data, indent=2)}")

            seen_first_tick[sec_id] = True

        # -----------------------------
        # 📈 LTP LOGGING (CLEAN FORMAT)
        # -----------------------------
        if config.get("SHOW_LTP"):
            ltp_raw = data.get("LTP")

            if ltp_raw is None:
                return

            ltp = float(ltp_raw)
            name = SECURITY_NAME_MAP.get(str(sec_id), "UNKNOWN")

            # 🔥 Price movement tracking
            if sec_id in prev_price_map:
                diff = ltp - prev_price_map[sec_id]
                arrow = "⬆️" if diff > 0 else "⬇️" if diff < 0 else "➡️"
            else:
                arrow = "➡️"

            prev_price_map[sec_id] = ltp

            print(f"📈 {name:<10} | ID: {sec_id} | LTP: {ltp} {arrow}")

    except Exception as e:
        print(f"❌ [{sec_id}] Parse Error:", e)


def on_error(ws, error, sec_id):
    print(f"🟠 [{sec_id}] ERROR:", error)


def on_close(ws, close_status_code, close_msg, sec_id):
    print(f"🔴 [{sec_id}] CLOSED → Reconnecting...")
    time.sleep(2)
    start_ws(sec_id)


def on_open(ws, sec_id):
    print(f"🟢 [{sec_id}] CONNECTED")

    subscribe_msg = {
        "RequestCode": 15,
        "InstrumentCount": 1,
        "InstrumentList": [
            {
                "ExchangeSegment": 0,
                "SecurityId": int(sec_id)
            }
        ]
    }

    try:
        ws.send(json.dumps(subscribe_msg))
        print(f"📡 [{sec_id}] SUBSCRIBED")
    except Exception as e:
        print(f"❌ [{sec_id}] Subscription Error:", e)


def start_ws(sec_id):
    ws_url = f"{BASE_URL}/{sec_id}/quote"

    print(f"🔌 Connecting to {ws_url}")

    ws = websocket.WebSocketApp(
        ws_url,
        on_open=lambda ws: on_open(ws, sec_id),
        on_message=lambda ws, msg: on_message(ws, msg, sec_id),
        on_error=lambda ws, err: on_error(ws, err, sec_id),
        on_close=lambda ws, code, msg: on_close(ws, code, msg, sec_id),
    )

    ws.run_forever()


def start_all():
    print("🔥 start_all() EXECUTED")
    print("\n📡 Initializing WebSocket Feeds...\n")

    for sec in SECURITIES:
        print(f"🚀 Starting feed for Security {sec}")

        t = threading.Thread(target=start_ws, args=(sec,), daemon=True)
        t.start()

    # ✅ Keep process alive
    while True:
        time.sleep(1)