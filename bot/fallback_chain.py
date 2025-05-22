# fallback_chain.py
import os
import asyncio
from faq_search import find_best_faq
from gpt4all import GPT4All
import openai

# Указываем точный путь к файлу

gpt4all_model = GPT4All(
    model_name="mistral-7b.Q4_K_M",                 # имя модели (без .gguf)
    model_path="/models",                           # только путь до папки
    allow_download=False
)

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_fallback_answer(query: str) -> str:
    """
    Пытается найти ответ сначала по FAQ, если не найден — возвращает сообщение для передачи админу.
    """
    faq_answer = find_best_faq(query)
    if faq_answer:
        return faq_answer
    return "Вибачте, я не знайшов відповіді. Ваше питання буде передано адміністратору."

async def get_bot_reply(message: str) -> str:
    try:
        faq_answer = await asyncio.to_thread(get_faq_answer, message)
        if faq_answer:
            print("[DEBUG] FAQ match found")
            return f"[FAQ] {faq_answer}"
    except Exception as e:
        print("[ERROR] FAQ search failed:", e)

    try:
        local_response = await asyncio.to_thread(
            gpt4all_model.generate, message, max_tokens=200
        )
        if local_response and len(local_response.strip()) > 10:
            print("[DEBUG] GPT4All fallback used")
            return f"[GPT4All] {local_response.strip()}"
    except Exception as e:
        print("[ERROR] GPT4All error:", e)

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
        )
        print("[DEBUG] ChatGPT fallback used")
        return f"[ChatGPT] {completion.choices[0].message.content.strip()}"
    except Exception as e:
        print("[ERROR] OpenAI error:", e)

    return "Извините, я не смог найти ответ на ваш вопрос."
