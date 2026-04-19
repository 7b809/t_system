import websocket
import json
import threading
import time

from ws_feed.price_store import update_price
from django.conf import settings


BASE_URL = "wss://sr-webhook.up.railway.app/ws"
SECURITIES = ["13", "21", "51", "5024"]

seen_first_tick = {}


def get_config():
    return getattr(settings, "WS_FEED_CONFIG", {})


def log(msg, level="INFO"):
    config = get_config()

    if config.get("TEST_LOG"):
        print(msg)
    elif config.get("SHOW_LTP") and level == "LTP":
        print(msg)
    # else → silent


def on_message(ws, message, sec_id):
    try:
        data = json.loads(message)

        update_price(sec_id, data)

        # ✅ First tick
        if not seen_first_tick.get(sec_id):
            log(f"✅ [{sec_id}] FIRST DATA RECEIVED")
            seen_first_tick[sec_id] = True

        config = get_config()

        if config.get("TEST_LOG"):
            print(f"📥 [{sec_id}] SAMPLE DATA:\n{json.dumps(data, indent=2)}")

        elif config.get("SHOW_LTP"):
            log(f"[{sec_id}] LTP: {data.get('LTP')}", level="LTP")

    except Exception as e:
        print(f"❌ [{sec_id}] Parse Error:", e)  # always show errors


def on_error(ws, error, sec_id):
    print(f"🟠 [{sec_id}] ERROR:", error)  # always show


def on_close(ws, close_status_code, close_msg, sec_id):
    print(f"🔴 [{sec_id}] CLOSED → Reconnecting...")
    time.sleep(2)
    start_ws(sec_id)


def on_open(ws, sec_id):
    log(f"🟢 [{sec_id}] CONNECTED")

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
        log(f"📡 [{sec_id}] SUBSCRIBED")
    except Exception as e:
        print(f"❌ [{sec_id}] Subscription Error:", e)


def start_ws(sec_id):
    ws_url = f"{BASE_URL}/{sec_id}/quote"

    log(f"🔌 Connecting to {ws_url}")

    ws = websocket.WebSocketApp(
        ws_url,
        on_open=lambda ws: on_open(ws, sec_id),
        on_message=lambda ws, msg: on_message(ws, msg, sec_id),
        on_error=lambda ws, err: on_error(ws, err, sec_id),
        on_close=lambda ws, code, msg: on_close(ws, code, msg, sec_id),
    )

    ws.run_forever()


def start_all():
    print("🔥 start_all() EXECUTED")  # always print (important debug)

    log("\n📡 Initializing WebSocket Feeds...\n")

    threads = []

    for sec in SECURITIES:
        log(f"🚀 Starting feed for Security {sec}")

        t = threading.Thread(target=start_ws, args=(sec,), daemon=True)
        t.start()
        threads.append(t)

    # ❌ DO NOT use join() here
    # ✅ Keep thread alive safely
    while True:
        time.sleep(1)