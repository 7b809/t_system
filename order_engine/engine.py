from ws_feed.price_store import get_price

RANGE = 10  # points


def should_place_order(alert):
    """
    Decide whether to place order based on:
    - Alert price
    - Live market price (from WebSocket)
    - security_id (passed from URL)

    Expected alert:
    {
        'price': '22450',
        'type': 'buyPE',
        'security_id': '21'
    }
    """

    try:
        # 🔹 Validate inputs
        if 'price' not in alert:
            return False, "Missing price in alert"

        if 'security_id' not in alert:
            return False, "Missing security_id (from URL)"

        alert_price = float(alert['price'])
        sec_id = str(alert['security_id'])

        # 🔹 Get live data from WebSocket store
        live_data = get_price(sec_id)

        if not live_data:
            return False, f"No live data for security_id={sec_id}"

        # 🔹 Extract LTP
        ltp_raw = live_data.get("LTP")

        if ltp_raw is None:
            return False, f"LTP missing in feed for {sec_id}"

        ltp = float(ltp_raw)

        # 🔹 Compare price range
        diff = abs(ltp - alert_price)

        print(f"📊 Compare | Sec: {sec_id} | Alert: {alert_price} | LTP: {ltp} | Diff: {diff}")

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