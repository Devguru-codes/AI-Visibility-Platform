"""
Startup script for the AI Visibility Platform frontend
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    frontend_app = Path(__file__).parent / "frontend" / "app.py"
    
    print("Starting AI Visibility Platform Frontend...")
    print("Dashboard will open at: http://localhost:8501")
    print("\nPress Ctrl+C to stop\n")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(frontend_app)])
