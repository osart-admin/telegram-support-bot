# bot/faq_search.py

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "/app/db/faq_index.pkl"
THRESHOLD = 0.7  # минимальная близость для совпадения

# Загружаем индекс и модель
with open(INDEX_PATH, "rb") as f:
    questions, embeddings = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_faq_answer(query: str) -> str | None:
    query_vec = model.encode([query])
    similarities = cosine_similarity(query_vec, embeddings)[0]

    best_match_idx = int(np.argmax(similarities))
    best_score = similarities[best_match_idx]

    if best_score >= THRESHOLD:
        return questions[best_match_idx]
    return None
