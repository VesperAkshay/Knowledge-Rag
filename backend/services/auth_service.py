"""
Authentication and session management
"""
from typing import Optional, Dict
from backend.database.db import UserDB, SessionDB, CredentialsDB


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def register_user(username: str, password: str) -> Dict:
        """Register a new user"""
        if len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters"}
        
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        user_id = UserDB.create_user(username, password)
        
        if not user_id:
            return {"success": False, "error": "Username already exists"}
        
        return {
            "success": True,
            "user_id": user_id,
            "username": username
        }
    
    @staticmethod
    def login(username: str, password: str) -> Dict:
        """Login user and create session"""
        user_id = UserDB.authenticate(username, password)
        
        if not user_id:
            return {"success": False, "error": "Invalid username or password"}
        
        # Update last login
        UserDB.update_last_login(user_id)
        
        # Create session
        session_id = SessionDB.create_session(user_id)
        
        # Check if user has credentials
        has_creds = CredentialsDB.has_credentials(user_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "username": username,
            "has_credentials": has_creds
        }
    
    @staticmethod
    def logout(session_id: str):
        """Logout user"""
        SessionDB.invalidate_session(session_id)
    
    @staticmethod
    def get_user_from_session(session_id: str) -> Optional[str]:
        """Get user_id from session"""
        return SessionDB.validate_session(session_id)
    
    @staticmethod
    def save_user_credentials(
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str
    ) -> Dict:
        """Save user's API credentials"""
        try:
            CredentialsDB.save_credentials(
                user_id,
                google_api_key,
                chromadb_api_key,
                chromadb_tenant,
                chromadb_database
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_user_credentials(user_id: str) -> Optional[Dict]:
        """Get user's API credentials"""
        return CredentialsDB.get_credentials(user_id)


# Global instance
auth_service = AuthService()
