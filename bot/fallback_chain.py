# bot/fallback_chain.py

import os
import asyncio
from gpt4all import GPT4All
import openai
from faq_search import find_best_faq

# Инициализация модели GPT4All
model_path = "/models"
model_name = "mistral-7b.Q4_K_M"
gpt4all_model = GPT4All(model_name=model_name, model_path=model_path, allow_download=False)

# Ключ OpenAI (если настроен)
openai.api_key = os.getenv("OPENAI_API_KEY")


async def get_fallback_answer(query: str) -> str:
    # Сначала пробуем найти по FAQ (повторно, fallback на всякий случай)
    try:
        faq_answer = find_best_faq(query)
        if faq_answer:
            return faq_answer
    except Exception as e:
        print("[ERROR] FAQ fallback failed:", e)

    # Пытаемся получить ответ от GPT4All
    try:
        local_response = await asyncio.to_thread(
            gpt4all_model.generate,
            query,
            max_tokens=200
        )
        if local_response and len(local_response.strip()) > 10:
            print("[DEBUG] GPT4All fallback used")
            return f"[GPT4All] {local_response.strip()}"
    except Exception as e:
        print("[ERROR] GPT4All error:", e)

    # Пытаемся получить ответ от OpenAI
    try:
        completion = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-4",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
        )
        print("[DEBUG] ChatGPT fallback used")
        return f"[ChatGPT] {completion.choices[0].message.content.strip()}"
    except Exception as e:
        print("[ERROR] OpenAI error:", e)

    return "Вибачте, я не знайшов відповіді. Ваше питання буде передано адміністратору."
