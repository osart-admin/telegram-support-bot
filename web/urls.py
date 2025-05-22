# web/urls.py
from django.http import JsonResponse
from django.contrib import admin
from django.urls import path

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

urlpatterns = [
    path("debug/headers", debug_headers),
    path("admin/", admin.site.urls),
]
