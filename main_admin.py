from __future__ import annotations
import uvicorn
from app.admin.app import app
from app.core.config import settings


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
