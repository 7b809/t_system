from django.shortcuts import render
from django.core.paginator import Paginator
from order_engine.engine import get_all_orders

def home(request):
    orders = get_all_orders()
    orders = sorted(orders, key=lambda x: x.get("timestamp", ""), reverse=True)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "orders_dashboard.html", {
        "page_obj": page_obj
    })


def live_dashboard(request):
    return render(request, "live_dashboard.html")