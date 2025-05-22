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

OUTPUT = "/app/db/faq_index.pkl"
os.makedirs("db", exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")

conn = mysql.connector.connect(**DB)
cursor = conn.cursor()
cursor.execute("SELECT question, answer FROM supportapp_faq")
rows = cursor.fetchall()
conn.close()

questions = []
answers = []

for q, a in rows:
    questions.append(f"{q}\n{a}")
    answers.append(a)

embeddings = model.encode(questions, normalize_embeddings=True)

# Сохраняем именно как (questions, embeddings)
with open(OUTPUT, "wb") as f:
    pickle.dump((questions, embeddings), f)

print(f"[+] Saved {len(questions)} FAQs to {OUTPUT}")

