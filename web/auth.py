# web/auth.py

import hashlib
import os
import mysql.connector
from fastapi import Request, HTTPException, status
from starlette.responses import RedirectResponse

def authenticate_user(username: str, password: str) -> bool:
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "mysql"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "support")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash = result[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return stored_hash == password_hash

        return False
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return False

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
