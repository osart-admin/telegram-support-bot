# bot/embedding.py

import os
import faiss
import pymysql
import numpy as np
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv
load_dotenv()

# Подключение к БД через переменные окружения
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "support")

DB_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

model = SentenceTransformer("all-MiniLM-L6-v2")
engine = create_engine(DB_URL)

class FAQIndex:
    def __init__(self):
        self.index = faiss.IndexFlatL2(384)  # 384 для all-MiniLM-L6-v2
        self.questions = []
        self.answers = []
        self._load_data()

    def _load_data(self):
        with engine.connect() as conn:
            result = conn.execute("SELECT question, answer FROM supportapp_faq")
            data = result.fetchall()
        if not data:
            return

        questions, answers = zip(*data)
        embeddings = model.encode(list(questions), convert_to_numpy=True)
        self.index.add(embeddings)
        self.questions = questions
        self.answers = answers

    def search(self, query, top_k=1):
        query_vec = model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(query_vec, top_k)
        if D[0][0] > 1.0:
            return None  # Слишком далеко
        return self.answers[I[0][0]]

faq_index = FAQIndex()

def get_faq_answer(query):
    return faq_index.search(query)
