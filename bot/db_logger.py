import os
import MySQLdb
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "user": os.getenv("MYSQL_USER", "root"),
    "passwd": os.getenv("MYSQL_PASSWORD", ""),
    "db": os.getenv("MYSQL_DATABASE", "support"),
    "charset": "utf8mb4",
}

def get_connection():
    return MySQLdb.connect(**DB_CONFIG)

def log_message(user_id: int, message: str, direction: str, thread_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO supportapp_message (thread_id, sender, text, created_at)
        VALUES (%s, %s, %s, NOW())
    """, (thread_id, direction, message))
    conn.commit()
    cursor.close()
    conn.close()

def update_message_status(thread_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE supportapp_messagethread SET status = %s WHERE id = %s
    """, (status, thread_id))
    conn.commit()
    cursor.close()
    conn.close()

def create_or_update_thread(user_id: int, message: str, user_data: dict = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM supportapp_messagethread
        WHERE user_id = %s AND resolved = FALSE
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()

    if user_data:
        first_name = user_data.get("first_name")
        last_name = user_data.get("last_name")
        username = user_data.get("username")
        photo_url = user_data.get("photo_url")
    else:
        first_name = last_name = username = photo_url = None

    if result:
        thread_id = result[0]
        cursor.execute("""
            UPDATE supportapp_messagethread
            SET first_name = %s, last_name = %s, username = %s, photo_url = %s, last_message_at = NOW()
            WHERE id = %s
        """, (first_name, last_name, username, photo_url, thread_id))
        conn.commit()
    else:
        cursor.execute("""
            INSERT INTO supportapp_messagethread
            (user_id, first_name, last_name, username, photo_url, last_message_at, status, created_at, resolved)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s, NOW(), FALSE)
        """, (user_id, first_name, last_name, username, photo_url, "новое"))
        conn.commit()
        thread_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return thread_id

def close_message_thread(thread_id: int, mark_as_faq: bool = False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE supportapp_messagethread SET resolved = TRUE, status = 'закрыто' WHERE id = %s
    """, (thread_id,))
    conn.commit()
    cursor.close()
    conn.close()

def save_faq(question: str, answer: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO supportapp_faq (question, answer) VALUES (%s, %s)
    """, (question, answer))
    conn.commit()
    cursor.close()
    conn.close()
