# -----------------------------------
# 📦 PRICE STORE (ENHANCED)
# -----------------------------------

latest_prices = {}


# -----------------------------------
# 🔄 UPDATE PRICE (NO CHANGE IN LOGIC)
# -----------------------------------
def update_price(security_id, data):
    """
    Store full websocket data
    """
    latest_prices[security_id] = data


# -----------------------------------
# 📥 GET FULL DATA (EXISTING)
# -----------------------------------
def get_price(security_id):
    """
    Return full stored data
    """
    return latest_prices.get(security_id)


# -----------------------------------
# 🔥 NEW: GET LTP ONLY (ADDED)
# -----------------------------------
def get_ltp(security_id, default=None):
    """
    Safely extract LTP from stored data
    """
    data = latest_prices.get(security_id)

    if not data:
        return default

    try:
        ltp = data.get("LTP")
        return float(ltp) if ltp is not None else default
    except Exception:
        return default


# -----------------------------------
# 🔥 NEW: CHECK IF DATA EXISTS
# -----------------------------------
def has_price(security_id):
    """
    Check if we have price data for given security
    """
    return security_id in latest_prices


# -----------------------------------
# 🔥 NEW: GET ALL PRICES (DEBUG / ANALYTICS)
# -----------------------------------
def get_all_prices():
    """
    Return entire price map
    """
    return latest_prices


# -----------------------------------
# 🔥 NEW: CLEAR STORE (OPTIONAL)
# -----------------------------------
def clear_prices():
    """
    Reset all stored prices
    """
    latest_prices.clear()