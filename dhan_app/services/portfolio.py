from .client import get_dhan_client


def get_holdings():
    client = get_dhan_client()

    if not client:
        return None

    return client.get_holdings()


def get_positions():
    client = get_dhan_client()

    if not client:
        return None

    return client.get_positions()


def get_orders():
    client = get_dhan_client()

    if not client:
        return None

    return client.get_order_list()