# bot/search.py
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import openai
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("faq_index.faiss")
data = pickle.load(open("faq_data.pkl", "rb"))

openai.api_key = os.getenv("OPENAI_API_KEY")

def find_answer(query):
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, k=1)
    if D[0][0] < 1.0:
        return data[I[0][0]]["answer"]
    else:
        return fallback_chatgpt(query)

def fallback_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]
