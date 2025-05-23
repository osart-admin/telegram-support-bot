# web/supportapp/signals.py

import os
import subprocess
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FAQ

logger = logging.getLogger(__name__)

@receiver([post_save, post_delete], sender=FAQ)
def rebuild_faq_index(sender, **kwargs):
    try:
        logger.info("Обнаружено изменение в FAQ. Перестраиваем индекс...")
        subprocess.Popen(["python", "embeddings/build_index.py"], cwd="/app")
    except Exception as e:
        logger.error(f"Не удалось обновить индекс FAQ: {e}", exc_info=True)
