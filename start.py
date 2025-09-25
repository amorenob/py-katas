#!/usr/bin/env python3
""" Launcher for Kata Exercise.
Usage:
    python start.py
"""

from app import app  # FastAPI instance

def main():
    print("Kata Exercise")
    print("Launching at http://localhost:8000\n")
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError as e:
        print("Missing dependency:", e)
        print("Install deps first, e.g.: pip install -r requirements.txt")
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    main()