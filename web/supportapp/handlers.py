from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from telegram import Bot
import os
import logging

logger = logging.getLogger(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

@receiver(post_save, sender=Message)
def send_admin_response(sender, instance, created, **kwargs):
    if not created or instance.sender != "admin":
        return

    try:
        if bot:
            bot.send_message(
                chat_id=instance.thread.user_id,
                text=f"✉️ Адміністратор відповів:\n\n{instance.text}",
                parse_mode="HTML"
            )
            logger.info(f"[+] Ответ администратора отправлен пользователю {instance.thread.user_id}")
        else:
            logger.warning("Telegram бот не настроен.")
    except Exception as e:
        logger.error(f"[ERROR] Не удалось отправить сообщение: {e}", exc_info=True)
