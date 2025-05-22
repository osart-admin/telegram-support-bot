# bot/faq_search.py

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "/app/db/faq_index.pkl"
THRESHOLD = 0.3  # минимальная близость для совпадения

# Загружаем модель и индекс
model = SentenceTransformer("all-MiniLM-L6-v2")

with open(INDEX_PATH, "rb") as f:
    pairs, embeddings = pickle.load(f)
    # pairs: list of (question, answer)

def find_best_faq(query: str) -> str | None:
    query_vec = model.encode([query])
    similarities = cosine_similarity(query_vec, embeddings)[0]

    best_idx = int(np.argmax(similarities))
    best_score = similarities[best_idx]

    if best_score >= THRESHOLD:
        question, answer = pairs[best_idx]
        return f"[FAQ] {answer}"
    return None
