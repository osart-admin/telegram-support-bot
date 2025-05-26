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
from fallback_chain import get_bot_reply

bot = Bot(
    token=os.getenv("TELEGRAM_BOT_TOKEN"),
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

    # Передаём флаг is_voice=True!
    await handle_message_logic(message, text, is_voice=True)

@dp.message(lambda m: m.text)
async def handle_message(message: types.Message):
    await handle_message_logic(message, message.text, is_voice=False)

async def handle_message_logic(message: types.Message, text: str, is_voice: bool = False):
    user = message.from_user
    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "photo_url": f"https://t.me/i/userpic/320/{user.username}.jpg" if user.username else None
    }
    thread_id = create_or_update_thread(user.id, text, user_data=user_data)
    log_message(user_id=user.id, message=text, direction="user", thread_id=thread_id)

    # Сначала ищем по FAQ
    response = find_best_faq(text)
    is_faq = response is not None

    if not is_faq:
        # Ответ от OpenAI
        response = await get_bot_reply(text)
        # Если в ответе нет уже префикса, добавим [GPT]
        if not response.startswith("[GPT]"):
            response = f"[GPT] {response}"

    log_message(user_id=user.id, message=response, direction="admin", thread_id=thread_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Допомогло", callback_data=f"helped:{thread_id}")
    kb.button(text="❌ Не допомогло", callback_data=f"not_helped:{thread_id}")

    # Формируем текст для ответа
    if is_voice:
        result_text = (
            "<b>Голосове повідомлення</b>\n"
            f"<i>{text}</i>\n\n"
            f"{response}"
        )
    else:
        result_text = response

    await message.reply(result_text, reply_markup=kb.as_markup(), parse_mode="HTML")

@dp.callback_query(lambda c: c.data.startswith("helped"))
async def handle_helped(callback_query: types.CallbackQuery):
    thread_id = int(callback_query.data.split(":")[1])
    close_message_thread(thread_id)
    await bot.send_message(callback_query.from_user.id, "Дякуємо за звернення!")

@dp.callback_query(lambda c: c.data.startswith("not_helped"))
async def handle_not_helped(callback_query: types.CallbackQuery):
    thread_id = int(callback_query.data.split(":")[1])
    await bot.send_message(callback_query.from_user.id, "Ваш запит передано адміністратору. Очікуйте відповідь.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
