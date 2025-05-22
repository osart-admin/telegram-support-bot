# bot/vector_store.py
from sentence_transformers import SentenceTransformer
import faiss
import pickle

data = [
    {"question": "Как восстановить пароль?", "answer": "Перейдите по ссылке восстановления..."},
    {"question": "Как изменить имя пользователя?", "answer": "Это можно сделать в настройках профиля."},
]

model = SentenceTransformer("all-MiniLM-L6-v2")
questions = [item["question"] for item in data]
embeddings = model.encode(questions)

index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(embeddings)

with open("faq_index.faiss", "wb") as f:
    faiss.write_index(index, f)
with open("faq_data.pkl", "wb") as f:
    pickle.dump(data, f)
