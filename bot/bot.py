# bot/bot.py

import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties

from db_logger import log_message, create_or_update_thread, close_message_thread, save_faq
from transcribe import transcribe_audio
from faq_search import find_best_faq
from fallback_chain import get_fallback_answer

bot = Bot(
    token=os.getenv("TELEGRAM_TOKEN"),
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

@dp.message(lambda m: m.voice)
async def handle_voice(message: types.Message):
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

    tmp_ogg = f"/tmp/{message.voice.file_unique_id}.ogg"
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            with open(tmp_ogg, "wb") as f:
                f.write(await response.read())

    text = transcribe_audio(tmp_ogg)
    os.remove(tmp_ogg)

    if not text:
        await message.reply("Пожалуйста, отправьте текстовое сообщение.")
        return

    await handle_message_logic(message, text)

@dp.message(lambda m: m.text)
async def handle_message(message: types.Message):
    await handle_message_logic(message, message.text)

async def handle_message_logic(message: types.Message, text: str):
    user_id = message.from_user.id
    thread_id = create_or_update_thread(user_id, text)
    log_message(user_id=user_id, message=text, direction="user", thread_id=thread_id)

    response = find_best_faq(text)
    if response is None:
        response = await get_fallback_answer(text)

    log_message(user_id=user_id, message=response, direction="admin", thread_id=thread_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Допомогло", callback_data=f"helped:{thread_id}")
    kb.button(text="❌ Не допомогло", callback_data=f"not_helped:{thread_id}")
    await message.reply(response, reply_markup=kb.as_markup(), parse_mode=None)  # <-- fix здесь

@dp.callback_query(lambda c: c.data.startswith("helped"))
async def handle_helped(callback_query: types.CallbackQuery):
    thread_id = int(callback_query.data.split(":")[1])
    close_message_thread(thread_id)
    await bot.send_message(callback_query.from_user.id, "Дякуємо за звернення!")

@dp.callback_query(lambda c: c.data.startswith("not_helped"))
async def handle_not_helped(callback_query: types.CallbackQuery):
    thread_id = int(callback_query.data.split(":")[1])
    # можно логировать как "потребуется ручная доработка"
    await bot.send_message(callback_query.from_user.id, "Ваш запит передано адміністратору. Очікуйте відповідь.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
