"""
Configuration Management
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Keys
    GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")
    CHROMADB_API_KEY: str = os.environ.get("CHROMADB_API_KEY", "")
    CHROMADB_TENANT: str = os.environ.get("CHROMADB_TENANT", "")
    CHROMADB_DATABASE: str = os.environ.get("CHROMADB_DATABASE", "")
    LANGSMITH_API_KEY: str = os.environ.get("LANGSMITH_API_KEY", "")
    
    # Model Settings
    LLM_MODEL: str = "gemini-2.5-flash-lite"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_TEMPERATURE: float = 0.7
    
    # Vector Store Settings
    COLLECTION_NAME: str = "unified_knowledge_base"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_K: int = 3
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database name (for logging)
    DATABASE_NAME: str = os.environ.get("CHROMADB_DATABASE", "Rag-Knoeledge")
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    
    # Application Info
    APP_TITLE: str = "Orchestrator RAG Knowledge Base"
    APP_DESCRIPTION: str = "Smart RAG system with web search fallback"
    APP_VERSION: str = "2.0.0"

# Global settings instance
settings = Settings()
