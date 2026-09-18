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
    role: str

import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from email_validator import EmailNotValidError, validate_email

ph = PasswordHasher()

def get_password_hash(password: str) -> str:
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def validate_password_strength(password: str) -> None:
    if len(password) < 12 or len(password) > 128:
        raise ValueError("Password must be between 12 and 128 characters.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain at least one special character.")
    if "\x00" in password or password.strip() != password:
        raise ValueError("Password contains invalid characters or leading/trailing whitespace.")

class AuthService:
    @staticmethod
    def create_user(full_name: str, email: str, password: str) -> UserInfo:
        # Validate email
        try:
            valid_email = validate_email(email, check_deliverability=False)
            email = valid_email.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e!s}")

        # Validate password
        validate_password_strength(password)

        conn = get_db()
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(password)
        now = time.time()
        
        try:
            cursor.execute(
                "INSERT INTO users (id, full_name, email, password_hash, created_at, role) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, full_name, email, hashed_password, now, "OWNER")
            )
            
            # Initialize onboarding status
            cursor.execute(
                "INSERT INTO onboarding_status (user_id, is_complete, current_step) VALUES (?, ?, ?)",
                (user_id, False, 1)
            )
            
            conn.commit()
            return UserInfo(id=user_id, full_name=full_name, email=email, role="OWNER")
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")
        finally:
            conn.close()

    @staticmethod
    def authenticate_user(email: str, password: str) -> UserInfo | None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, password_hash, role FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        if not verify_password(password, row['password_hash']):
            return None
            
        return UserInfo(id=row['id'], full_name=row['full_name'], email=row['email'], role=row['role'])

    @staticmethod
    def create_session(user_id: str) -> tuple[str, str]:
        token = str(uuid.uuid4())
        csrf_token = str(uuid.uuid4())
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
        return token, csrf_token

    @staticmethod
    def invalidate_session(token: str) -> None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        
    @staticmethod
    def invalidate_all_sessions(user_id: str) -> None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        
    @staticmethod
    def generate_password_reset_token(email: str) -> str | None:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None # Don't reveal user existence, but we internally know it didn't do anything
            
        user_id = row['id']
        token = str(uuid.uuid4())
        now = time.time()
        expires_at = now + (15 * 60) # 15 minutes
        
        cursor.execute(
            "INSERT INTO password_resets (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, now, expires_at)
        )
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def reset_password(token: str, new_password: str) -> bool:
        validate_password_strength(new_password)
        hashed_password = get_password_hash(new_password)
        now = time.time()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM password_resets WHERE token = ? AND expires_at > ?", (token, now))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
            
        user_id = row['user_id']
        
        # Update password
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
        
        # Invalidate the reset token
        cursor.execute("DELETE FROM password_resets WHERE token = ?", (token,))
        
        # Invalidate all existing sessions
        cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True
        
    @staticmethod
    def get_user_from_token(token: str) -> UserInfo | None:
        if not token:
            return None
            
        conn = get_db()
        cursor = conn.cursor()
        now = time.time()
        
        cursor.execute("""
            SELECT u.id, u.full_name, u.email, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token, now))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return UserInfo(id=row['id'], full_name=row['full_name'], email=row['email'], role=row['role'])


def get_current_user(session: str | None = Cookie(None)) -> UserInfo:
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = AuthService.get_user_from_token(session)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
        
    return user
