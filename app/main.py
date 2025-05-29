from fastapi import FastAPI

from . import models
from .db import engine
from .routes import api_router

app = FastAPI(title="Messaging System API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Messaging System API!"}


@app.get("/health")
async def death_check():
    return {"status": "ok"}
