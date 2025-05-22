import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def send_admin_response(sender, instance, created, **kwargs):
    if instance.response and not created:
        try:
            from telegram import Bot
            TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
            if TELEGRAM_TOKEN:
                bot = Bot(token=TELEGRAM_TOKEN)
                bot.send_message(
                    chat_id=instance.user_id,
                    text=f"👤 Администратор відповів:\n\n{instance.response}",
                    parse_mode="HTML"
                )
            else:
                logger.warning("TELEGRAM_TOKEN is not set")
        except Exception as e:
            logger.error(f"Ошибка при отправке ответа: {e}")
