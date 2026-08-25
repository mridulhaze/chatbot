import os
import uvicorn
from backend.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting National University AI Assistant on http://{host}:{port}")
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)