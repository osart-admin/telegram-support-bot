# web/urls.py
import os
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.urls import path
from django.views.static import serve

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

# Favicon для DEBUG=True, чтобы не падало, если STATIC_ROOT не задан
if settings.DEBUG:
    FAVICON_PATH = os.path.join(settings.BASE_DIR, "static", "favicon.ico")
    urlpatterns = [
        path('favicon.ico', serve, {'path': FAVICON_PATH}),
    ]
else:
    urlpatterns = []

urlpatterns += [
    path("", index),
    path("debug/headers", debug_headers),
    path("admin/", admin.site.urls),
]
