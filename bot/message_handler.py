# bot/message_handler.py
import asyncio
from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from fallback_chain import get_bot_reply

router = Router()

@router.message(F.text)
async def handle_text_message(message: Message, state: FSMContext):
    user_text = message.text.strip()
    await message.answer("🤖 Думаю...")

    try:
        reply = await get_bot_reply(user_text)
        await message.answer(reply)
    except Exception as e:
        print("[ERROR] handle_text_message:", e)
        await message.answer("Произошла ошибка при обработке сообщения.")
