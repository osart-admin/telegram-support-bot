# bot/utils/user_utils.py

import os
import requests
from supportapp.models import MessageThread
from aiogram import types

def fetch_avatar_file_id(user_id: int) -> str | None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUserProfilePhotos",
            params={"user_id": user_id, "limit": 1}, timeout=5
        )
        r.raise_for_status()
        data = r.json()
        if data.get("ok") and data["result"]["total_count"] > 0:
            return data["result"]["photos"][0][0]["file_id"]
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch avatar for {user_id}: {e}")
    return None

def process_user_info(user: types.User) -> MessageThread:
    thread, created = MessageThread.objects.get_or_create(
        user_id=user.id,
        defaults={
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_file_id": fetch_avatar_file_id(user.id),
        }
    )

    updated = False
    for attr in ["username", "first_name", "last_name"]:
        new_val = getattr(user, attr, None)
        if new_val and getattr(thread, attr) != new_val:
            setattr(thread, attr, new_val)
            updated = True

    if not thread.avatar_file_id:
        file_id = fetch_avatar_file_id(user.id)
        if file_id:
            thread.avatar_file_id = file_id
            updated = True

    if updated:
        thread.save()

    return thread
