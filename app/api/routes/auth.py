import os

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.middleware.request_id import request_id_ctx_var
from app.services.auth_service import AuthService, UserInfo, get_current_user

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

def _set_auth_cookie(response: Response, token: str):
    is_secure = os.getenv("PHYSICA_ENV") == "production"
    response.set_cookie(key="session", value=token, httponly=True, secure=is_secure, samesite="lax", max_age=30*24*60*60)

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, response: Response):
    try:
        user = AuthService.create_user(data.full_name, data.email, data.password)
        token, csrf_token = AuthService.create_session(user.id)
        
        _set_auth_cookie(response, token)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False, # Must be readable by frontend for Double Submit Cookie
            samesite="lax",
            secure=True,
            max_age=30 * 24 * 60 * 60
        )
        return {"user": user.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, response: Response):
    user = AuthService.authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    token, csrf_token = AuthService.create_session(user.id)
    _set_auth_cookie(response, token)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        samesite="lax",
        secure=os.getenv("PHYSICA_ENV") == "production",
        max_age=30 * 24 * 60 * 60
    )
    return {"user": user.model_dump()}

@router.post("/logout")
async def logout(response: Response, session: str | None = Cookie(None)):
    if session:
        AuthService.invalidate_session(session)
    response.delete_cookie("session")
    response.delete_cookie("csrf_token")
    return {"status": "ok"}

@router.post("/forgot-password")
@limiter.limit("5/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    _ = AuthService.generate_password_reset_token(data.email)
    # In a real system, send email here using the token
    # For now, we just pretend it succeeded so we don't leak account existence
    req_id = request_id_ctx_var.get()
    return {"message": "If an account exists, a password reset link has been sent.", "request_id": req_id}

@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPasswordRequest):
    try:
        success = AuthService.reset_password(data.token, data.new_password)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        return {"message": "Password has been reset successfully. Please log in with your new password."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
def get_me(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    return user
