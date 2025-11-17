"""
Database models and setup
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict
import secrets
import hashlib

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "rag_users.db")


def get_db():
    """Get database connection with timeout"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable write-ahead logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # User credentials table (encrypted API keys)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            google_api_key TEXT,
            chromadb_api_key TEXT,
            chromadb_tenant TEXT,
            chromadb_database TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id)
        )
    """)
    
    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            message_id TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash


def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"user_{secrets.token_urlsafe(16)}"


def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"session_{secrets.token_urlsafe(32)}"


class UserDB:
    """User database operations"""
    
    @staticmethod
    def create_user(username: str, password: str) -> Optional[str]:
        """Create a new user"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            user_id = generate_user_id()
            password_hash = hash_password(password)
            
            cursor.execute(
                "INSERT INTO users (user_id, username, password_hash) VALUES (?, ?, ?)",
                (user_id, username, password_hash)
            )
            
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[str]:
        """Authenticate user and return user_id"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, password_hash FROM users WHERE username = ?",
            (username,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user["password_hash"]):
            return user["user_id"]
        return None
    
    @staticmethod
    def update_last_login(user_id: str):
        """Update user's last login timestamp"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE user_id = ?",
            (datetime.now().isoformat(), user_id)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, username, created_at, last_login FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None


class CredentialsDB:
    """User credentials database operations"""
    
    @staticmethod
    def save_credentials(
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str
    ):
        """Save or update user credentials"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO user_credentials 
            (user_id, google_api_key, chromadb_api_key, chromadb_tenant, chromadb_database, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                google_api_key = excluded.google_api_key,
                chromadb_api_key = excluded.chromadb_api_key,
                chromadb_tenant = excluded.chromadb_tenant,
                chromadb_database = excluded.chromadb_database,
                updated_at = excluded.updated_at
            """,
            (user_id, google_api_key, chromadb_api_key, chromadb_tenant, 
             chromadb_database, datetime.now())
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_credentials(user_id: str) -> Optional[Dict]:
        """Get user credentials"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT google_api_key, chromadb_api_key, chromadb_tenant, chromadb_database
            FROM user_credentials WHERE user_id = ?
            """,
            (user_id,)
        )
        
        creds = cursor.fetchone()
        conn.close()
        
        if creds:
            return dict(creds)
        return None
    
    @staticmethod
    def has_credentials(user_id: str) -> bool:
        """Check if user has saved credentials"""
        creds = CredentialsDB.get_credentials(user_id)
        return creds is not None


class SessionDB:
    """Session database operations"""
    
    @staticmethod
    def create_session(user_id: str, expires_hours: int = 24) -> str:
        """Create a new session"""
        from datetime import timedelta
        
        conn = get_db()
        cursor = conn.cursor()
        
        session_id = generate_session_id()
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        cursor.execute(
            "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
            (session_id, user_id, expires_at)
        )
        
        conn.commit()
        conn.close()
        return session_id
    
    @staticmethod
    def validate_session(session_id: str) -> Optional[str]:
        """Validate session and return user_id"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT user_id, expires_at, is_active 
            FROM sessions WHERE session_id = ?
            """,
            (session_id,)
        )
        
        session = cursor.fetchone()
        conn.close()
        
        if not session or not session["is_active"]:
            return None
        
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            SessionDB.invalidate_session(session_id)
            return None
        
        return session["user_id"]
    
    @staticmethod
    def invalidate_session(session_id: str):
        """Invalidate a session"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE sessions SET is_active = 0 WHERE session_id = ?",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def cleanup_expired_sessions():
        """Remove expired sessions"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM sessions WHERE expires_at < ? OR is_active = 0",
            (datetime.now(),)
        )
        
        conn.commit()
        conn.close()


class ChatHistoryDB:
    """Chat history database operations"""
    
    @staticmethod
    def save_message(user_id: str, message_id: str, role: str, content: str):
        """Save a chat message"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO chat_history (user_id, message_id, role, content) VALUES (?, ?, ?, ?)",
            (user_id, message_id, role, content)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_history(user_id: str, limit: int = 50) -> list:
        """Get user's chat history"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT message_id, role, content, timestamp 
            FROM chat_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (user_id, limit)
        )
        
        messages = cursor.fetchall()
        conn.close()
        
        return [dict(msg) for msg in reversed(messages)]
    
    @staticmethod
    def clear_user_history(user_id: str):
        """Clear user's chat history"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM chat_history WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        conn.close()


# Initialize database on import
init_db()

# Create instances
chat_history_db = ChatHistoryDB()
