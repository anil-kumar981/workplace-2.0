import uvicorn
from app import app

__all__ = ["app"]

if __name__ == "__main__":
    # Start uvicorn server dynamically if run directly via 'python main.py'
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
