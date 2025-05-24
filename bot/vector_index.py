# bot/vector_index.py

import os
import numpy as np
import faiss
from sqlalchemy import create_engine, MetaData, Table, select
from sentence_transformers import SentenceTransformer

# Читаем переменные окружения (совпадают с docker-compose/.env)
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "support")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

# Строка подключения
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

metadata = MetaData()
faq_table = Table("supportapp_faq", metadata, autoload_with=engine)

model = SentenceTransformer("all-MiniLM-L6-v2")

with engine.connect() as conn:
    rows = conn.execute(select(faq_table)).fetchall()

questions = [row.question for row in rows]
answers = [row.answer for row in rows]

if not questions:
    print("[WARN] Нет вопросов для индексации! База пустая.")
    embeddings = np.zeros((0, 384), dtype="float32")  # Размерность для MiniLM
else:
    embeddings = model.encode(questions, convert_to_numpy=True, normalize_embeddings=True)

# Cоздаём FAISS-индекс
if len(embeddings) > 0:
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, "/app/db/faq_faiss.index")
    np.save("/app/db/faq_embeddings.npy", embeddings)
else:
    print("[WARN] Пустой FAISS-индекс не будет сохранён.")

# Сохраняем ответы (чтобы быстро по индексу искать текст)
with open("/app/db/faq_answers.txt", "w", encoding="utf-8") as f:
    for answer in answers:
        f.write(answer.replace("\n", " ") + "\n")

print(f"✅ Индекс успешно построен. Всего вопросов: {len(questions)}")
