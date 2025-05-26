# bot/fallback_chain.py

from faq_search import find_best_faq
from ai_utils import ask_gpt_openai

async def get_bot_reply(query: str) -> str:
    # 1. Пробуем найти ответ по FAQ
    try:
        faq_answer = find_best_faq(query)
        if faq_answer:
            return faq_answer
    except Exception as e:
        print("[ERROR] FAQ search failed:", e)

    # 2. Fallback: спрашиваем у OpenAI gpt-4.1-mini
    try:
        ai_response = await ask_gpt_openai(query)
        return ai_response
    except Exception as e:
        print("[ERROR] OpenAI error:", e)

    return "Вибачте, я не знайшов відповіді. Ваше питання буде передано адміністратору."
