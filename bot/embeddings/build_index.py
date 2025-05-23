# bot/embeddings/build_index.py

import os
import pickle
import mysql.connector
from sentence_transformers import SentenceTransformer

DB = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "support"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

OUTPUT = "/app/db/faq_index.pkl"  # или './db/faq_index.pkl'
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

conn = mysql.connector.connect(**DB)
cursor = conn.cursor()
cursor.execute("SELECT question, answer FROM supportapp_faq")
rows = cursor.fetchall()
conn.close()

questions = []
answers = []

for q, a in rows:
    questions.append(q)
    answers.append(a)

print(f"[DEBUG] Всего вопросов для индексации: {len(questions)}")
for i, q in enumerate(questions):
    print(f"  {i+1}: {q}")

embeddings = model.encode(questions, normalize_embeddings=True)

# 💾 сохраняем как (questions, answers, embeddings)
with open(OUTPUT, "wb") as f:
    pickle.dump((questions, answers, embeddings), f)

print(f"[+] Saved {len(questions)} FAQs to {OUTPUT}")
