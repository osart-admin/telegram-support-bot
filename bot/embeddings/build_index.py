# embeddings/build_index.py
import os
import faiss
import mysql.connector
from sentence_transformers import SentenceTransformer
import numpy as np

DB = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "support"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
}

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = mysql.connector.connect(**DB)
cursor = conn.cursor()
cursor.execute("SELECT id, question, answer FROM supportapp_faq")
data = cursor.fetchall()

ids, texts, answers = [], [], []
for id_, q, a in data:
    ids.append(id_)
    texts.append(q)
    answers.append(a)

embeddings = model.encode(texts, convert_to_numpy=True)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, "embeddings/index.faiss")
np.save("embeddings/id_map.npy", np.array(ids))
np.save("embeddings/answers.npy", np.array(answers))

print("[+] Index rebuilt. Vector count:", len(ids))
