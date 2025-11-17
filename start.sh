#!/bin/bash
# Production startup script for Render

# Create necessary directories
mkdir -p uploads
mkdir -p chroma_db
mkdir -p backend/database

# Start the FastAPI server
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
