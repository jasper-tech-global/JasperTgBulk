from __future__ import annotations
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import init_db
from . import auth, routes


app = FastAPI(title="Jasper TG BULK Admin")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


app.include_router(auth.router)
app.include_router(routes.router)
