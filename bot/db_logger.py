# bot/db_logger.py

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


def create_or_update_thread(user_id: int, message: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    # Найдём активный тред
    cursor.execute("""
        SELECT id FROM supportapp_messagethread
        WHERE user_id = %s AND resolved = FALSE
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()

    if result:
        thread_id = result[0]
    else:
        cursor.execute("""
            INSERT INTO supportapp_messagethread (user_id, status, created_at, resolved)
            VALUES (%s, %s, NOW(), FALSE)
        """, (user_id, "новое"))
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

    if mark_as_faq:
        cursor.execute("""
            SELECT text FROM supportapp_message
            WHERE thread_id = %s AND sender = 'user'
            ORDER BY created_at ASC LIMIT 1
        """, (thread_id,))
        question = cursor.fetchone()
        cursor.execute("""
            SELECT text FROM supportapp_message
            WHERE thread_id = %s AND sender = 'admin'
            ORDER BY created_at DESC LIMIT 1
        """, (thread_id,))
        answer = cursor.fetchone()

        if question and answer:
            cursor.execute("""
                INSERT INTO supportapp_faq (question, answer) VALUES (%s, %s)
            """, (question[0], answer[0]))

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
