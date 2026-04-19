from django.urls import path
from .views import tradingview_webhook, tradingview_webhook_with_id

urlpatterns = [
    path('tradingview/', tradingview_webhook),
    path('tradingview/<str:security_id>/', tradingview_webhook_with_id),
]