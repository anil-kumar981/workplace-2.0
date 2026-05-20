import uvicorn
from app import app
from app.core import config

__all__ = ["app"]

if __name__ == "__main__":
    # Start uvicorn server dynamically using configurations loaded from environment
    uvicorn.run("main:app", host=config.IP_ADDRESS, port=config.PORT, reload=True)

