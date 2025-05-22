import os
import numpy as np
import faiss
from sqlalchemy import create_engine, MetaData, Table, select
from sentence_transformers import SentenceTransformer

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_NAME = os.getenv("DB_NAME", "support")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
metadata = MetaData()
faq_table = Table("supportapp_faq", metadata, autoload_with=engine)

model = SentenceTransformer("all-MiniLM-L6-v2")

with engine.connect() as conn:
    rows = conn.execute(select(faq_table)).fetchall()

questions = [row.question for row in rows]
answers = [row.answer for row in rows]

embeddings = model.encode(questions, convert_to_numpy=True)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

np.save("db/faq_embeddings.npy", embeddings)
with open("db/faq_answers.txt", "w") as f:
    for answer in answers:
        f.write(answer.replace("\n", " ") + "\n")

print("✅ Индекс успешно построен.")
