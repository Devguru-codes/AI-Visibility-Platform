"""
Startup script for the AI Visibility Platform backend
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Now run
import uvicorn

if __name__ == "__main__":
    print("Starting AI Visibility Platform Backend...")
    print("API will be available at: http://localhost:8001")
    print("API docs at: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop\n")
    
    # Use string reference for reload to work
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
