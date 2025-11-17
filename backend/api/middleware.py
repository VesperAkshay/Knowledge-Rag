"""
Authentication middleware
"""
from fastapi import Request, HTTPException, Cookie
from typing import Optional, Callable
from backend.services.auth_service import auth_service


async def get_current_user_id(request: Request) -> Optional[str]:
    """Get current user ID from session cookie"""
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        return None
    
    user_id = auth_service.get_user_from_session(session_id)
    return user_id


async def require_auth(request: Request) -> str:
    """Require authentication, raise exception if not authenticated"""
    user_id = await get_current_user_id(request)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return user_id


async def require_credentials(request: Request) -> dict:
    """Require authentication and credentials"""
    user_id = await require_auth(request)
    
    creds = auth_service.get_user_credentials(user_id)
    
    if not creds:
        raise HTTPException(
            status_code=403,
            detail="API credentials not configured. Please add your credentials first."
        )
    
    # Return combined dict with user_id and all credentials
    return {
        "user_id": user_id,
        "google_api_key": creds["google_api_key"],
        "chromadb_api_key": creds["chromadb_api_key"],
        "chromadb_tenant": creds["chromadb_tenant"],
        "chromadb_database": creds["chromadb_database"]
    }
