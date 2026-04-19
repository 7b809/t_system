from django.core.management.base import BaseCommand
from ws_feed.ws_client import start_all


class Command(BaseCommand):
    help = "Run WebSocket Feed Listener"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting WebSocket feeds..."))
        start_all()