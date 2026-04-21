import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings  # ✅ NEW

from .services import process_alert

# 🔹 Direct flag (no helper function)
BASIC_LOGS = os.getenv("BASIC_LOGS", "false").lower() == "true"


@csrf_exempt
def tradingview_webhook(request):
    """
    Default endpoint (no security_id)
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # ✅ Inject defaults (NO LOGIC CHANGE)
            data["mode"] = data.get("mode", getattr(settings, "DEFAULT_MODE", "PAPER"))
            data["force_order"] = data.get(
                "force_order",
                getattr(settings, "DEFAULT_FORCE_ORDER", True)
            )

            # 🔹 Conditional logging
            if BASIC_LOGS:
                print("📩 Incoming Webhook:", data)

            result = process_alert(data)

            if BASIC_LOGS:
                print("✅ Processed Result:", result)

            return JsonResponse({
                "status": "success",
                "processed": result
            })

        except Exception as e:
            if BASIC_LOGS:
                print("❌ Error:", str(e))

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

            # ✅ Inject defaults (NO LOGIC CHANGE)
            data["mode"] = data.get("mode", getattr(settings, "DEFAULT_MODE", "PAPER"))
            data["force_order"] = data.get(
                "force_order",
                getattr(settings, "DEFAULT_FORCE_ORDER", True)
            )

            if BASIC_LOGS:
                print(f"📩 Incoming for Security {security_id}:", data)

            result = process_alert(data)

            if BASIC_LOGS:
                print(f"✅ Processed Result for {security_id}:", result)

            return JsonResponse({
                "status": "success",
                "security_id": security_id,
                "processed": result
            })

        except Exception as e:
            if BASIC_LOGS:
                print(f"❌ Error for {security_id}:", str(e))

            return JsonResponse({"error": str(e)}, status=400)