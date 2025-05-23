# bot/faq_search.py

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

INDEX_PATH = "/app/db/faq_index.pkl"  # или './db/faq_index.pkl' — смотри по своему проекту
THRESHOLD = 0.7  # debug threshold для чувствительности

model = SentenceTransformer("all-MiniLM-L6-v2")

questions = answers = embeddings = None
index_mtime = 0

def load_index():
    global questions, answers, embeddings, index_mtime
    try:
        mtime = os.path.getmtime(INDEX_PATH)
        if questions is None or mtime > index_mtime:
            with open(INDEX_PATH, "rb") as f:
                questions, answers, embeddings = pickle.load(f)
            index_mtime = mtime
            logger.info(f"[faq_search] FAQ-индекс обновлён, записей: {len(questions)}")
            print("[DEBUG] Загруженные вопросы FAQ:")
            for i, q in enumerate(questions):
                print(f"  {i+1}: {q}")
    except Exception as e:
        logger.error(f"[faq_search] Ошибка при загрузке индекса FAQ: {e}")
        print(f"[faq_search] Ошибка при загрузке индекса FAQ: {e}")

def find_best_faq(query: str) -> str | None:
    print(f"[DEBUG] Входящий запрос: '{query}'")
    load_index()
    if questions is None or embeddings is None:
        print("[DEBUG] FAQ индекс не загружен")
        return None
    query_vec = model.encode([query])
    similarities = cosine_similarity(query_vec, embeddings)[0]

    print("[DEBUG] Схожести запроса с каждым вопросом FAQ:")
    for i, score in enumerate(similarities):
        print(f"  {i+1}: '{questions[i][:60]}...' — {score:.4f}")

    best_match_idx = int(np.argmax(similarities))
    best_score = similarities[best_match_idx]
    print(f"[DEBUG] Лучший индекс: {best_match_idx} (схожесть {best_score:.4f}) — вопрос: '{questions[best_match_idx]}'")

    if best_score >= THRESHOLD:
        print(f"[DEBUG] Совпадение выше порога ({THRESHOLD}) — возврат FAQ")
        return f"[FAQ] {answers[best_match_idx]}"
    else:
        print(f"[DEBUG] Совпадение ниже порога ({THRESHOLD}) — FAQ не найден")
    return None
