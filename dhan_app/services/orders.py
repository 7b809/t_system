from .client import get_dhan_client


def place_order(security_id, price, qty=1, order_type="MARKET"):
    client = get_dhan_client()

    if not client:
        return {"status": "error", "msg": "No client"}

    try:
        response = client.place_order(
            security_id=int(security_id),
            exchange_segment="NSE_FNO",
            transaction_type="BUY",
            quantity=qty,
            order_type=order_type,
            product_type="INTRADAY",
            price=price
        )

        print("✅ Order placed:", response)

        return response

    except Exception as e:
        print("❌ Order error:", e)
        return {"status": "error", "msg": str(e)}


def exit_order(order_id):
    client = get_dhan_client()

    try:
        response = client.cancel_order(order_id)
        return response
    except Exception as e:
        return {"error": str(e)}