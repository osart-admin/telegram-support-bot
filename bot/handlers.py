from aiogram import types, Dispatcher

async def start_handler(message: types.Message):
    await message.answer("Привет! Отправь мне голосовое сообщение.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"])
