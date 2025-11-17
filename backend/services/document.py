"""
Document Upload and Processing Service
Handles file uploads and URL scraping
"""
import os
import logging
from typing import List
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader,
    UnstructuredWordDocumentLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.core.config import settings
from backend.services.vector_store import vector_store_service

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document upload and processing"""
    
    def __init__(self):
        """Initialize document service"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )
    
    async def process_file(
        self,
        file_path: str,
        filename: str,
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str
    ) -> dict:
        """
        Process an uploaded file and index it to user's knowledge base
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            user_id: User ID
            google_api_key: User's Google API key
            chromadb_api_key: User's ChromaDB API key
            chromadb_tenant: User's ChromaDB tenant
            chromadb_database: User's ChromaDB database
            
        Returns:
            dict: Processing results with chunk count
        """
        logger.info(f"📄 User {user_id} - Processing file: {filename}")
        
        try:
            # Determine loader based on file extension
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif ext in ['.doc', '.docx']:
                loader = UnstructuredWordDocumentLoader(file_path)
            elif ext == '.txt':
                loader = TextLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            
            logger.info(f"🔍 Loading document with {loader.__class__.__name__}")
            documents = loader.load()
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"✂️ Split into {len(chunks)} chunks")
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata.update({
                    "source": filename,
                    "uploaded_at": datetime.now().isoformat(),
                    "type": "file_upload"
                })
            
            # Index chunks to user's collection
            vector_store_service.index_documents(
                user_id=user_id,
                google_api_key=google_api_key,
                chromadb_api_key=chromadb_api_key,
                chromadb_tenant=chromadb_tenant,
                chromadb_database=chromadb_database,
                documents=chunks
            )
            logger.info(f"✅ User {user_id} - Successfully indexed {len(chunks)} chunks")
            
            return {
                "success": True,
                "filename": filename,
                "chunks": len(chunks),
                "message": f"Successfully processed and indexed {len(chunks)} chunks"
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing file {filename}: {str(e)}")
            raise
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🗑️ Cleaned up temporary file: {file_path}")
    
    async def process_url(
        self,
        url: str,
        user_id: str,
        google_api_key: str,
        chromadb_api_key: str,
        chromadb_tenant: str,
        chromadb_database: str
    ) -> dict:
        """
        Scrape and process a URL to user's knowledge base
        
        Args:
            url: URL to scrape
            user_id: User ID
            google_api_key: User's Google API key
            chromadb_api_key: User's ChromaDB API key
            chromadb_tenant: User's ChromaDB tenant
            chromadb_database: User's ChromaDB database
            
        Returns:
            dict: Processing results with chunk count
        """
        logger.info(f"🌐 User {user_id} - Processing URL: {url}")
        
        try:
            # Scrape URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks_text = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks_text if chunk)
            
            logger.info(f"📝 Extracted {len(text)} characters from URL")
            
            # Create document
            from langchain_core.documents import Document
            doc = Document(
                page_content=text,
                metadata={
                    "source": url,
                    "domain": urlparse(url).netloc,
                    "uploaded_at": datetime.now().isoformat(),
                    "type": "url_upload"
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            logger.info(f"✂️ Split into {len(chunks)} chunks")
            
            # Index chunks to user's collection
            vector_store_service.index_documents(
                user_id=user_id,
                google_api_key=google_api_key,
                chromadb_api_key=chromadb_api_key,
                chromadb_tenant=chromadb_tenant,
                chromadb_database=chromadb_database,
                documents=chunks
            )
            logger.info(f"✅ User {user_id} - Successfully indexed {len(chunks)} chunks from URL")
            
            return {
                "success": True,
                "url": url,
                "chunks": len(chunks),
                "message": f"Successfully scraped and indexed {len(chunks)} chunks"
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing URL {url}: {str(e)}")
            raise


# Global instance
document_service = DocumentService()
