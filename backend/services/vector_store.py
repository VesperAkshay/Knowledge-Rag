"""
Vector Store Service
Handles ChromaDB operations
"""
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Optional
from datetime import datetime
from pydantic import SecretStr

from backend.core.config import settings


class VectorStoreService:
    """Service for vector store operations"""
    
    def __init__(self):
        """Initialize vector store service"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            add_start_index=True,
        )
    
    def _get_chroma_client(
        self,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str
    ):
        """Get a ChromaDB client with user credentials"""
        import logging
        logger = logging.getLogger(__name__)
        
        # If credentials look like cloud credentials, try CloudClient
        # ChromaDB Cloud keys typically start with 'ck-' or other prefixes
        if chromadb_api_key and len(chromadb_api_key) > 10 and chromadb_api_key.startswith(('ck-', 'sk-', 'token-', 'chroma-')):
            try:
                logger.info(f"Attempting ChromaDB Cloud connection for tenant: {chromadb_tenant}")
                return chromadb.CloudClient(
                    tenant=chromadb_tenant,
                    database=chromadb_database,
                    api_key=chromadb_api_key
                )
            except Exception as e:
                logger.warning(f"ChromaDB Cloud connection failed: {e}. Falling back to local client.")
        
        # Fallback to local persistent client
        logger.info(f"Using local ChromaDB client for user data")
        persist_directory = f"./chroma_db/{chromadb_tenant}_{chromadb_database}"
        return chromadb.PersistentClient(path=persist_directory)
    
    def _get_user_collection_name(self, user_id: str) -> str:
        """Get user-specific collection name"""
        return f"{user_id}_unified_knowledge_base"
    
    def get_or_create_collection(
        self,
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str,
        collection_name: Optional[str] = None
    ) -> Chroma:
        """Get or create a user-specific vector store collection"""
        # Use user-specific collection name
        collection_name = collection_name or self._get_user_collection_name(user_id)
        
        # Get user-specific client and embeddings
        chroma_client = self._get_chroma_client(
            chromadb_api_key,
            chromadb_tenant,
            chromadb_database
        )
        
        # Create embeddings with user's Google API key
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=SecretStr(google_api_key)
        )
        
        try:
            collection = chroma_client.get_collection(collection_name)
        except:
            collection = chroma_client.create_collection(collection_name)
        
        vector_store = Chroma(
            client=chroma_client,
            collection_name=collection_name,
            embedding_function=embeddings
        )
        return vector_store
    
    def index_document(
        self,
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str,
        content: str, 
        metadata: dict,
        collection_name: Optional[str] = None
    ) -> int:
        """Index a document into the user's knowledge base"""
        doc = Document(page_content=content, metadata=metadata)
        chunks = self.text_splitter.split_documents([doc])
        
        vector_store = self.get_or_create_collection(
            user_id=user_id,
            google_api_key=google_api_key,
            chromadb_api_key=chromadb_api_key,
            chromadb_tenant=chromadb_tenant,
            chromadb_database=chromadb_database,
            collection_name=collection_name
        )
        vector_store.add_documents(chunks)
        
        return len(chunks)
    
    def index_documents(
        self,
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str,
        documents: list,
        collection_name: Optional[str] = None
    ) -> int:
        """Index multiple documents into the user's knowledge base"""
        vector_store = self.get_or_create_collection(
            user_id=user_id,
            google_api_key=google_api_key,
            chromadb_api_key=chromadb_api_key,
            chromadb_tenant=chromadb_tenant,
            chromadb_database=chromadb_database,
            collection_name=collection_name
        )
        vector_store.add_documents(documents)
        return len(documents)
    
    def get_collection_count(
        self,
        user_id: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str,
        collection_name: Optional[str] = None
    ) -> int:
        """Get document count in user's collection"""
        collection_name = collection_name or self._get_user_collection_name(user_id)
        try:
            chroma_client = self._get_chroma_client(
                chromadb_api_key,
                chromadb_tenant,
                chromadb_database
            )
            collection = chroma_client.get_collection(collection_name)
            return collection.count()
        except:
            return 0
    
    def clear_collection(
        self,
        user_id: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str,
        collection_name: Optional[str] = None
    ):
        """Clear all documents from user's collection"""
        collection_name = collection_name or self._get_user_collection_name(user_id)
        chroma_client = self._get_chroma_client(
            chromadb_api_key,
            chromadb_tenant,
            chromadb_database
        )
        chroma_client.delete_collection(collection_name)


# Global instance
vector_store_service = VectorStoreService()
