import hashlib
import sqlite3
import time
import uuid

from fastapi import Cookie, HTTPException
from pydantic import BaseModel

from app.db.database import get_db


class UserInfo(BaseModel):
    id: str
    full_name: str
    email: str

def get_password_hash(password: str) -> str:
    # A simple deterministic hash for local demo. Do NOT use in production.
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

class AuthService:
    @staticmethod
    def create_user(full_name: str, email: str, password: str) -> UserInfo:
        conn = get_db()
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(password)
        now = time.time()
        
        try:
            cursor.execute(
                "INSERT INTO users (id, full_name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, full_name, email, hashed_password, now)
            )
            
            # Initialize onboarding status
            cursor.execute(
                "INSERT INTO onboarding_status (user_id, is_complete, current_step) VALUES (?, ?, ?)",
                (user_id, False, 1)
            )
            
            conn.commit()
            return UserInfo(id=user_id, full_name=full_name, email=email)
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")
        finally:
            conn.close()

    @staticmethod
    def authenticate_user(email: str, password: str) -> UserInfo | None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, password_hash FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        if not verify_password(password, row['password_hash']):
            return None
            
        return UserInfo(id=row['id'], full_name=row['full_name'], email=row['email'])

    @staticmethod
    def create_session(user_id: str) -> str:
        token = str(uuid.uuid4())
        now = time.time()
        expires_at = now + (30 * 24 * 60 * 60) # 30 days
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, now, expires_at)
        )
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def invalidate_session(token: str) -> None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        
    @staticmethod
    def get_user_from_token(token: str) -> UserInfo | None:
        if not token:
            return None
            
        conn = get_db()
        cursor = conn.cursor()
        now = time.time()
        
        cursor.execute("""
            SELECT u.id, u.full_name, u.email 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token, now))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return UserInfo(id=row['id'], full_name=row['full_name'], email=row['email'])


def get_current_user(session: str | None = Cookie(None)) -> UserInfo:
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = AuthService.get_user_from_token(session)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
        
    return user
