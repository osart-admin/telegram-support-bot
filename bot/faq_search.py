# bot/faq_search.py

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "/app/db/faq_index.pkl"
THRESHOLD = 0.7

model = SentenceTransformer("all-MiniLM-L6-v2")

# Кэш
questions = answers = embeddings = None
index_mtime = 0

def load_index():
    global questions, answers, embeddings, index_mtime
    mtime = os.path.getmtime(INDEX_PATH)
    if questions is None or mtime > index_mtime:
        with open(INDEX_PATH, "rb") as f:
            questions, answers, embeddings = pickle.load(f)
        index_mtime = mtime

def find_best_faq(query: str) -> str | None:
    load_index()
    query_vec = model.encode([query])
    similarities = cosine_similarity(query_vec, embeddings)[0]
    best_match_idx = int(np.argmax(similarities))
    best_score = similarities[best_match_idx]

    if best_score >= THRESHOLD:
        return f"[FAQ] {answers[best_match_idx]}"
    return None
