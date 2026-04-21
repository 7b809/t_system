from django.http import JsonResponse
from order_engine.orders import get_all_orders
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def orders_api(request):
    orders = get_all_orders()

    orders = sorted(
        orders,
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )[:50]

    data = []
    for o in orders:
        utc_time = o.get("timestamp")

        formatted_time = None
        if utc_time:
            dt = datetime.fromisoformat(utc_time)
            dt_ist = dt.replace(tzinfo=pytz.utc).astimezone(IST)
            formatted_time = dt_ist.strftime("%d %b %Y, %I:%M:%S %p")

        data.append({
            "time": formatted_time,   # ✅ formatted IST
            "index": o.get("index_id"),
            "type": o.get("type"),
            "strike": o.get("strike"),
            "status": o.get("status"),
            "price": o.get("executed_price"),
            "mode": o.get("mode"),
        })

    return JsonResponse({"orders": data})