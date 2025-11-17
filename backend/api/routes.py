"""
API Routes
FastAPI endpoints for the application
"""
import logging
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Cookie, Depends
from fastapi.responses import StreamingResponse
from typing import Optional

from backend.core.models import (
    ChatRequest,
    ChatResponse,
    UploadURLRequest,
    UploadResponse,
    KnowledgeBaseInfo,
    HealthResponse
)
from backend.services.agent import agent_service
from backend.services.document import document_service
from backend.services.vector_store import vector_store_service
from backend.api.middleware import require_credentials
from backend.database.db import chat_history_db

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0"
    )


@router.get("/info", response_model=KnowledgeBaseInfo)
@router.get("/knowledge-base-info", response_model=KnowledgeBaseInfo)
async def get_knowledge_base_info(credentials: dict = Depends(require_credentials)):
    """Get user's knowledge base statistics"""
    user_id = credentials["user_id"]
    chromadb_api_key = credentials["chromadb_api_key"]
    chromadb_tenant = credentials["chromadb_tenant"]
    chromadb_database = credentials["chromadb_database"]
    
    count = vector_store_service.get_collection_count(
        user_id=user_id,
        chromadb_api_key=chromadb_api_key,
        chromadb_tenant=chromadb_tenant,
        chromadb_database=chromadb_database
    )
    return KnowledgeBaseInfo(document_count=count)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    credentials: dict = Depends(require_credentials)
):
    """
    Chat endpoint with orchestrator agent
    Handles knowledge base retrieval and web search
    Requires authentication and saved credentials
    """
    try:
        user_id = credentials["user_id"]
        google_api_key = credentials["google_api_key"]
        chromadb_api_key = credentials["chromadb_api_key"]
        chromadb_tenant = credentials["chromadb_tenant"]
        chromadb_database = credentials["chromadb_database"]
        
        logger.info(f"💬 User {user_id} - Chat request: {request.message[:50]}...")
        
        # Save user message to history
        import uuid
        user_msg_id = str(uuid.uuid4())
        chat_history_db.save_message(user_id, user_msg_id, "user", request.message)
        
        # Create agent with user-specific credentials
        agent, vector_store = agent_service.create_agent(
            user_id=user_id,
            google_api_key=google_api_key,
            chromadb_api_key=chromadb_api_key,
            chromadb_tenant=chromadb_tenant,
            chromadb_database=chromadb_database
        )
        
        # Invoke agent
        result = agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]}
        )
        
        # Extract response from result
        response_message = ""
        for msg in reversed(result["messages"]):
            if hasattr(msg, 'type') and msg.type == 'ai':
                response_message = msg.content
                break
        
        if not response_message:
            response_message = "No response generated"
        
        # Save assistant response to history
        assistant_msg_id = str(uuid.uuid4())
        chat_history_db.save_message(user_id, assistant_msg_id, "assistant", response_message)
        
        logger.info(f"✅ User {user_id} - Response: {response_message[:100]}...")
        return ChatResponse(response=response_message)
            
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    credentials: dict = Depends(require_credentials)
):
    """
    Upload and process a document file
    Supports PDF, DOCX, TXT formats
    Requires authentication and saved credentials
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        user_id = credentials["user_id"]
        google_api_key = credentials["google_api_key"]
        chromadb_api_key = credentials["chromadb_api_key"]
        chromadb_tenant = credentials["chromadb_tenant"]
        chromadb_database = credentials["chromadb_database"]
            
        logger.info(f"📤 User {user_id} - Received file upload: {file.filename}")
        
        # Save uploaded file temporarily in user-specific directory
        upload_dir = f"uploads/{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"💾 Saved file to: {file_path}")
        
        # Process file with user credentials
        result = await document_service.process_file(
            file_path,
            file.filename,
            user_id=user_id,
            google_api_key=google_api_key,
            chromadb_api_key=chromadb_api_key,
            chromadb_tenant=chromadb_tenant,
            chromadb_database=chromadb_database
        )
        
        return UploadResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-url", response_model=UploadResponse)
async def upload_url(
    request: UploadURLRequest,
    credentials: dict = Depends(require_credentials)
):
    """
    Scrape and process a URL
    Extracts text content and indexes it
    Requires authentication and saved credentials
    """
    try:
        user_id = credentials["user_id"]
        google_api_key = credentials["google_api_key"]
        chromadb_api_key = credentials["chromadb_api_key"]
        chromadb_tenant = credentials["chromadb_tenant"]
        chromadb_database = credentials["chromadb_database"]
        
        logger.info(f"🌐 User {user_id} - Received URL upload: {request.url}")
        
        # Process URL with user credentials
        result = await document_service.process_url(
            request.url,
            user_id=user_id,
            google_api_key=google_api_key,
            chromadb_api_key=chromadb_api_key,
            chromadb_tenant=chromadb_tenant,
            chromadb_database=chromadb_database
        )
        
        return UploadResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error uploading URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    credentials: dict = Depends(require_credentials)
):
    """
    Get user's chat history
    Returns list of past messages
    """
    try:
        user_id = credentials["user_id"]
        history = chat_history_db.get_user_history(user_id, limit)
        
        return {
            "success": True,
            "messages": history
        }
    except Exception as e:
        logger.error(f"❌ Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history")
async def clear_chat_history(credentials: dict = Depends(require_credentials)):
    """
    Clear user's chat history
    """
    try:
        user_id = credentials["user_id"]
        chat_history_db.clear_user_history(user_id)
        
        logger.info(f"🗑️ Cleared chat history for user {user_id}")
        return {
            "success": True,
            "message": "Chat history cleared"
        }
    except Exception as e:
        logger.error(f"❌ Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
