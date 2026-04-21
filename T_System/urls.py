from django.contrib import admin
from django.urls import path, include
from .views import home, live_dashboard
from order_engine.views import orders_api  # ✅ FIXED

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', include('webhook_app.urls')),
    path('ws/', include('ws_feed.urls')),

    path('', home),                     # 📊 Orders dashboard
    path('live/', live_dashboard),     # 📡 Live market dashboard
    path('api/orders/', orders_api),   # 🔥 API for interval fetch
]