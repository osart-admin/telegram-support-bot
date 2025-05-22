# bot/faq_search.py

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "/app/db/faq_index.pkl"
THRESHOLD = 0.8  # повысим до более реалистичного порога

with open(INDEX_PATH, "rb") as f:
    questions, answers, embeddings = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

def find_best_faq(query: str) -> str | None:
    query_vec = model.encode([query])
    similarities = cosine_similarity(query_vec, embeddings)[0]
    best_match_idx = int(np.argmax(similarities))
    best_score = similarities[best_match_idx]

    if best_score >= THRESHOLD:
        return f"[FAQ] {answers[best_match_idx]}"
    return None
