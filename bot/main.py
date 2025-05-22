import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from fallback_chain import get_bot_reply

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: Message):
    user_text = message.text.strip()
    logging.info(f"Incoming: {user_text}")

    reply = await get_bot_reply(user_text)
    logging.info(f"Reply: {reply}")

    await message.reply(reply)

if __name__ == "__main__":
    logging.info("Starting bot polling...")
    executor.start_polling(dp, skip_updates=True)
