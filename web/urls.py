# web/urls.py

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse, HttpResponse

def debug_headers(request):
    import logging
    logger = logging.getLogger("django")
    logger.warning("=== HEADERS ===")
    for k, v in request.META.items():
        if k.startswith("HTTP_") or k in ["REMOTE_ADDR", "SERVER_NAME", "SERVER_PORT"]:
            logger.warning(f"{k}: {v}")
    return JsonResponse({
        "META": {k: v for k, v in request.META.items() if k.startswith("HTTP_") or k in ["REMOTE_ADDR", "SERVER_NAME", "SERVER_PORT"]}
    })

def index(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path("", index),
    path("debug/headers", debug_headers),
    path("admin/", admin.site.urls),
]

# В режиме разработки Django сам отдаёт статику, favicon доступен по /static/favicon.ico
# В HTML-шаблоне (base.html/admin/base_site.html) пропиши:
# <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
