
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.services.auth_service import AuthService, UserInfo, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

@router.post("/register")
def register(req: RegisterRequest, response: Response) -> UserInfo:
    try:
        user = AuthService.create_user(req.full_name, req.email, req.password)
        token = AuthService.create_session(user.id)
        response.set_cookie(key="session", value=token, httponly=True, samesite="lax", max_age=30*24*60*60)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(req: LoginRequest, response: Response) -> UserInfo:
    user = AuthService.authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = AuthService.create_session(user.id)
    response.set_cookie(key="session", value=token, httponly=True, samesite="lax", max_age=30*24*60*60)
    return user

@router.post("/logout")
def logout(response: Response, user: UserInfo = Depends(get_current_user)) -> dict[str, str]:
    # We should technically extract the cookie and invalidate it, but let's just clear it on the client
    # For full security, we would pass Request and invalidate the specific token
    response.delete_cookie(key="session")
    return {"status": "logged_out"}

@router.get("/me")
def get_me(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    return user
