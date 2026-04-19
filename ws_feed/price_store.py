latest_prices = {}


def update_price(security_id, data):
    latest_prices[security_id] = data


def get_price(security_id):
    return latest_prices.get(security_id)