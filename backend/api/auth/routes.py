"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, Cookie, Response
from pydantic import BaseModel
from typing import Optional
from backend.services.auth_service import auth_service
from backend.database.db import UserDB

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class CredentialsRequest(BaseModel):
    google_api_key: str
    chromadb_api_key: str
    chromadb_tenant: str
    chromadb_database: str


@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user"""
    result = auth_service.register_user(request.username, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "user_id": result["user_id"],
        "username": result["username"],
        "message": "User registered successfully"
    }


@router.post("/login")
async def login(request: LoginRequest, response: Response):
    """Login user"""
    result = auth_service.login(request.username, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=result["session_id"],
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )
    
    return {
        "user_id": result["user_id"],
        "username": result["username"],
        "session_id": result["session_id"],
        "message": "Login successful"
    }


@router.post("/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    """Logout user"""
    if session_id:
        auth_service.logout(session_id)
    
    response.delete_cookie("session_id")
    return {"success": True}


@router.get("/me")
async def get_current_user(session_id: Optional[str] = Cookie(None)):
    """Get current user info"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = auth_service.get_user_from_session(session_id)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user = UserDB.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    has_creds = auth_service.get_user_credentials(user_id) is not None
    
    return {
        "user_id": user_id,
        "username": user["username"],
        "has_credentials": has_creds
    }


@router.post("/credentials")
async def save_credentials(
    request: CredentialsRequest,
    session_id: Optional[str] = Cookie(None)
):
    """Save user's API credentials"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = auth_service.get_user_from_session(session_id)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    result = auth_service.save_user_credentials(
        user_id,
        request.google_api_key,
        request.chromadb_api_key,
        request.chromadb_tenant,
        request.chromadb_database
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"success": True, "message": "Credentials saved successfully"}


@router.get("/credentials")
async def get_credentials(session_id: Optional[str] = Cookie(None)):
    """Get user's saved credentials (masked)"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = auth_service.get_user_from_session(session_id)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    creds = auth_service.get_user_credentials(user_id)
    
    if not creds:
        return {"has_credentials": False}
    
    # Mask sensitive data
    def mask_key(key: str) -> str:
        if len(key) > 8:
            return key[:4] + "*" * (len(key) - 8) + key[-4:]
        return "*" * len(key)
    
    return {
        "has_credentials": True,
        "google_api_key": mask_key(creds["google_api_key"]),
        "chromadb_api_key": mask_key(creds["chromadb_api_key"]),
        "chromadb_tenant": creds["chromadb_tenant"],
        "chromadb_database": creds["chromadb_database"]
    }
