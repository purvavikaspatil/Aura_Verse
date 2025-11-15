#!/usr/bin/env python3
"""
Simple script to start the FastAPI backend server.
Run this script to start the backend on http://localhost:8000
"""

import uvicorn
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Dynamic ETL Backend Server")
    print("=" * 60)
    print(f"Server will be available at: http://localhost:8000")
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        print("\nMake sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

