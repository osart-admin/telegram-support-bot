from aiogram import types, Dispatcher
from datetime import datetime
import django
import os
import sys

sys.path.append('/opt/telegram-support-bot/web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from supportapp.models import MessageThread

def get_or_create_thread(user: types.User):
    print(f"[DEBUG] Попытка сохранить {user.id} {user.username}")  # <- debug print 1
    print(f"[DEBUG] user: id={user.id} first_name={user.first_name} last_name={user.last_name} username={user.username}")  # <- debug print 2
    thread, _ = MessageThread.objects.get_or_create(user_id=user.id)
    thread.first_name = user.first_name
    thread.last_name = user.last_name
    thread.username = user.username
    thread.last_message_at = datetime.utcnow()
    if user.username:
        thread.photo_url = f"https://t.me/i/userpic/320/{user.username}.jpg"
    thread.save()
    return thread

async def start_handler(message: types.Message):
    get_or_create_thread(message.from_user)
    await message.answer("Привет! Отправь мне голосовое сообщение.")

async def any_message_handler(message: types.Message):
    get_or_create_thread(message.from_user)
    # Здесь логика обработки любого сообщения (текст, голосовое и т.д.)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"])
    dp.register_message_handler(any_message_handler)
