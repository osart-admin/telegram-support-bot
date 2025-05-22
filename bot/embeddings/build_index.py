# bot/embeddings/build_index.py

import os
import pickle
import mysql.connector
from sentence_transformers import SentenceTransformer

# Параметры подключения к MySQL
DB = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "support"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

OUTPUT = "/app/db/faq_index.pkl"
os.makedirs("/app/db", exist_ok=True)

# Загружаем модель
model = SentenceTransformer("all-MiniLM-L6-v2")

# Получаем данные из MySQL
conn = mysql.connector.connect(**DB)
cursor = conn.cursor()
cursor.execute("SELECT question, answer FROM supportapp_faq")
rows = cursor.fetchall()
conn.close()

# Формируем списки для индексации
pairs = []  # [(question, answer)]
texts = []  # для embeddings

for q, a in rows:
    pairs.append((q.strip(), a.strip()))
    texts.append(f"{q.strip()}\n{a.strip()}")

# Векторизация
embeddings = model.encode(texts, normalize_embeddings=True)

# Сохраняем как (pairs, embeddings)
with open(OUTPUT, "wb") as f:
    pickle.dump((pairs, embeddings), f)

print(f"[+] Saved {len(pairs)} FAQs to {OUTPUT}")
