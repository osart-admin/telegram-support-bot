import os
import sqlite3
from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import mysql.connector

from auth import authenticate_user, get_current_user

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MySQL конфигурация
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "user": os.getenv("MYSQL_USER", "support"),
    "password": os.getenv("MYSQL_PASSWORD", "supportpass"),
    "database": os.getenv("MYSQL_DATABASE", "support"),
}

@app.get("/")
def root(request: Request):
    return RedirectResponse(url="/login")

@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if authenticate_user(username, password):
        request.session["user"] = username
        return RedirectResponse(url="/panel", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"})

@app.get("/panel")
def panel(request: Request, user: str = Depends(get_current_user)):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT,
            message TEXT,
            status VARCHAR(255)
        )
    """)
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    messages = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("panel.html", {"request": request, "user": user, "messages": messages})

@app.post("/reply")
def reply(request: Request, message_id: int = Form(...), answer: str = Form(...), user: str = Depends(get_current_user)):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM messages WHERE id=%s", (message_id,))
    row = cursor.fetchone()
    if row:
        from aiogram import Bot
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        try:
            bot.send_message(chat_id=row[0], text=f"📬 Ответ оператора: {answer}")
        except:
            pass
        cursor.execute("UPDATE messages SET status='ответ отправлен' WHERE id=%s", (message_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/panel", status_code=status.HTTP_302_FOUND)

@app.get("/faq")
def faq_page(request: Request, user: str = Depends(get_current_user)):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT,
            answer TEXT
        )
    """)
    cursor.execute("SELECT * FROM faq")
    faqs = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("faq.html", {"request": request, "user": user, "faqs": faqs})

@app.post("/faq")
def add_faq(request: Request, question: str = Form(...), answer: str = Form(...), user: str = Depends(get_current_user)):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faq (question, answer) VALUES (%s, %s)", (question, answer))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/faq", status_code=status.HTTP_302_FOUND)

from hashlib import sha256
import hmac

@app.get("/tg-login")
def telegram_login(request: Request):
    data = dict(request.query_params)
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()) if k != "hash")
    secret_key = sha256(os.getenv("TELEGRAM_BOT_TOKEN").encode()).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), sha256).hexdigest()

    if data.get("hash") != valid_hash:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Ошибка подписи Telegram"})

    user_id = data.get("id")
    allowed_ids = os.getenv("ADMIN_USER_IDS", "").split(",")

    if str(user_id) not in allowed_ids:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Нет доступа"})

    request.session["user"] = f"tg_{user_id}"
    return RedirectResponse(url="/panel")
