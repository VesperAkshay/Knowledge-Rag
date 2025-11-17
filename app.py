"""
Orchestrator-Based Multi-Agent RAG System
Modular Architecture with Service Layer
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import backend modules
from backend.core.config import settings
from backend.api.routes import router
from backend.api.auth.routes import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description="Orchestrator-based RAG system with auto web search fallback",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - API is running"""
    return {
        "message": "Orchestrator RAG API is running",
        "version": "2.0.0",
        "frontend": "http://localhost:3000",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting {settings.APP_TITLE}")
    logger.info(f"📊 Model: {settings.LLM_MODEL}")
    logger.info(f"🗄️ Database: {settings.DATABASE_NAME}")
    logger.info(f"📚 Collection: {settings.COLLECTION_NAME}")
    logger.info(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
