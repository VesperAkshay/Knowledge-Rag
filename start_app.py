"""
Quick start script for the Multi-Agent RAG Application
"""

import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("🚀 Starting Multi-Agent RAG Knowledge Base")
    print("=" * 70)
    print()
    
    # Check environment
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Please create .env file with your API keys")
        return
    
    # Clear old API keys
    if sys.platform == "win32":
        os.system("powershell -Command \"Remove-Item Env:\\GOOGLE_API_KEY -ErrorAction SilentlyContinue\"")
    
    print("✅ Environment ready")
    print()
    print("📍 Application will be available at: http://localhost:8000")
    print("📊 API documentation at: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Run the app
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
