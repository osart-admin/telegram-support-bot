# web/supportapp/apps.py

from django.apps import AppConfig

class SupportappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "supportapp"

    def ready(self):
        import supportapp.handlers
        import supportapp.signals  # если добавляли сигнал автоперестроения FAQ
