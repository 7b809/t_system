import json
import os
import threading
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .services import process_alert
from core.db import get_order_mongo_client  # ✅ for error logging

# 🔹 Direct flag
BASIC_LOGS = os.getenv("BASIC_LOGS", "false").lower() == "true"


# -----------------------------------
# 🔥 ERROR LOGGER (Mongo)
# -----------------------------------
def log_webhook_error(raw_data, error_msg, security_id=None):
    try:
        client = get_order_mongo_client()
        db = client[settings.MONGO_DB_NAME]

        db.webhook_errors.insert_one({
            "error": error_msg,
            "payload": raw_data,
            "security_id": security_id,
            "time": datetime.utcnow()
        })
    except Exception as e:
        print("❌ Failed to log webhook error:", str(e))


# -----------------------------------
# ⚡ ASYNC PROCESSOR
# -----------------------------------
def run_async(data):
    try:
        process_alert(data)
    except Exception as e:
        print("❌ Async Processing Error:", str(e))


# -----------------------------------
# 🔹 DEFAULT WEBHOOK
# -----------------------------------
@csrf_exempt
def tradingview_webhook(request):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    raw = request.body.decode("utf-8", errors="ignore").strip()

    try:
        # ✅ Safe JSON parsing (no crash)
        try:
            data = json.loads(raw)
        except:
            data = {"raw_text": raw}

        # ✅ Inject defaults (UNCHANGED)
        data["mode"] = data.get("mode", getattr(settings, "DEFAULT_MODE", "PAPER"))
        data["force_order"] = data.get(
            "force_order",
            getattr(settings, "DEFAULT_FORCE_ORDER", True)
        )

        if BASIC_LOGS:
            print("📩 Incoming Webhook:", data)

        # ⚡ ASYNC execution (NO BLOCKING)
        threading.Thread(target=run_async, args=(data,)).start()

        return JsonResponse({
            "status": "accepted"
        })

    except Exception as e:
        if BASIC_LOGS:
            print("❌ Error:", str(e))

        # 🔥 Save error payload
        log_webhook_error(raw, str(e))

        return JsonResponse({"error": str(e)}, status=400)


# -----------------------------------
# 🔹 WEBHOOK WITH SECURITY ID
# -----------------------------------
@csrf_exempt
def tradingview_webhook_with_id(request, security_id):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    raw = request.body.decode("utf-8", errors="ignore").strip()

    try:
        # ✅ Safe JSON parsing
        try:
            data = json.loads(raw)
        except:
            data = {"raw_text": raw}

        # 🔥 Inject security_id (UNCHANGED)
        data["security_id"] = security_id

        # ✅ Inject defaults (UNCHANGED)
        data["mode"] = data.get("mode", getattr(settings, "DEFAULT_MODE", "PAPER"))
        data["force_order"] = data.get(
            "force_order",
            getattr(settings, "DEFAULT_FORCE_ORDER", True)
        )

        if BASIC_LOGS:
            print(f"📩 Incoming for Security {security_id}:", data)

        # ⚡ ASYNC execution
        threading.Thread(target=run_async, args=(data,)).start()

        return JsonResponse({
            "status": "accepted",
            "security_id": security_id
        })

    except Exception as e:
        if BASIC_LOGS:
            print(f"❌ Error for {security_id}:", str(e))

        # 🔥 Save error payload
        log_webhook_error(raw, str(e), security_id)

        return JsonResponse({"error": str(e)}, status=400)