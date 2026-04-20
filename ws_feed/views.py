from django.shortcuts import render

def live_dashboard(request):
    return render(request, "dashboard.html")