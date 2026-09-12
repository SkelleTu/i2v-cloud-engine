import os
from pathlib import Path

import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from main import app

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")

if __name__ == "__main__":
    uvicorn.run("launcher:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
