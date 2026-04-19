import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import process_alert


@csrf_exempt
def tradingview_webhook(request):
    """
    Default endpoint (no security_id)
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            result = process_alert(data)

            return JsonResponse({
                "status": "success",
                "processed": result
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def tradingview_webhook_with_id(request, security_id):
    """
    Dynamic endpoint with security_id
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # 🔥 Inject security_id into alert
            data["security_id"] = security_id

            print(f"📩 Incoming for Security {security_id}:", data)

            result = process_alert(data)

            return JsonResponse({
                "status": "success",
                "security_id": security_id,
                "processed": result
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)