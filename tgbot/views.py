import json
import logging

from django.http import JsonResponse
from django.views import View
from dtb.settings import DEBUG

from tgbot.dispatcher import process_telegram_event

logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return JsonResponse({"error": "sup hacker"})


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        process_telegram_event(json.loads(request.body))
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received! But nothing done"})
