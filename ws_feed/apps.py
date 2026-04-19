import os
import threading
from django.apps import AppConfig
from django.conf import settings


class WsFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ws_feed'

    def ready(self):

        if os.environ.get('RUN_MAIN') != 'true':
            return

        from ws_feed.ws_client import start_all

        print("\n==============================")
        print("🚀 Django System Booting...")
        print("📡 Starting WebSocket Feed...")
        print("==============================\n")

        def run_feed():
            try:
                print("🧵 Thread started → calling start_all()")
                start_all()
            except Exception as e:
                print("❌ WebSocket thread crashed:", e)

        thread = threading.Thread(target=run_feed, daemon=True)
        thread.start()