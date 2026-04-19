import re

def parse_alert_message(msg):
    """
    Example msg:
    Res_Hold Time=2026-04-19 10:30 Price=22450 Type=buyPE
    """

    # ✅ Extract event (first word)
    parts = msg.split(" ", 1)
    event = parts[0]

    # ✅ Extract Time (with space)
    time_match = re.search(r'Time=([\d\-]+\s[\d:]+)', msg)

    # ✅ Extract Price
    price_match = re.search(r'Price=([\d\.]+)', msg)

    # ✅ Extract Type
    type_match = re.search(r'Type=([a-zA-Z]+)', msg)

    return {
        "event": event,
        "time": time_match.group(1) if time_match else None,
        "price": price_match.group(1) if price_match else None,
        "type": type_match.group(1) if type_match else None,
    }