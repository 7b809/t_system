from django.urls import path
from .views import live_dashboard

urlpatterns = [
    path("dashboard/", live_dashboard, name="dashboard"),   # ✅ THIS LINE
]