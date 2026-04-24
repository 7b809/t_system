from django.http import JsonResponse
from order_engine.orders import get_all_orders
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def safe_get(value, fallback="-"):
    """Return fallback if value is None, empty, or invalid"""
    if value is None:
        return fallback
    if isinstance(value, str) and value.strip() == "":
        return fallback
    return value


def format_time(utc_time):
    """Convert UTC ISO time → IST formatted"""
    try:
        if not utc_time:
            return "-"

        dt = datetime.fromisoformat(utc_time)
        dt_ist = dt.replace(tzinfo=pytz.utc).astimezone(IST)
        return dt_ist.strftime("%d %b %Y, %I:%M:%S %p")

    except Exception:
        return "-"


def orders_api(request):
    try:
        orders = get_all_orders() or []

        # ✅ Sort latest first
        orders = sorted(
            orders,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )[:50]

        data = []

        for o in orders:
            data.append({
                # ✅ Time fields
                "time": format_time(o.get("timestamp")),
                "exit_time": format_time(o.get("exit_time")),

                # ✅ Core fields
                "index": safe_get(o.get("index_id")),
                "type": safe_get(o.get("type")),
                "strike": safe_get(o.get("strike")),
                "status": safe_get(o.get("status")),
                "mode": safe_get(o.get("mode")),

                # ✅ Prices
                "price": safe_get(o.get("executed_price")),   # executed price
                "alert_price": safe_get(o.get("alert_price")),
                "index_ltp": safe_get(o.get("index_ltp")),

                # ✅ Identifiers
                "order_id": safe_get(o.get("order_id")),
                "security_id": safe_get(o.get("security_id")),
            })

        return JsonResponse({
            "status": "success",
            "count": len(data),
            "orders": data
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "orders": []
        })