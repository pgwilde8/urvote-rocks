#!/usr/bin/env python3
"""
UrVote.Rocks Startup Script
Run this to start the FastAPI application
"""

import uvicorn
import os
from pathlib import Path

def main():
    """Main startup function"""
    
    # Set default configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    workers = int(os.getenv("WORKERS", "1"))
    
    # Ensure upload directory exists
    upload_dir = Path("/opt/urvote/uploads")
    upload_dir.mkdir(exist_ok=True)
    
    print(f"🚀 Starting UrVote.Rocks on {host}:{port}")
    print(f"📁 Upload directory: {upload_dir}")
    print(f"🔄 Auto-reload: {reload}")
    print(f"👥 Workers: {workers}")
    
    # Start the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info"
    )

if __name__ == "__main__":
    main()
