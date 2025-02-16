from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from .config import settings
from app.routers import conversation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    await init_db()
    yield
    # Shutdown: Clean up code here

app = FastAPI(
    title="LLM Conversations API",
    version="1.0.0",
    description="MVP Backend to manage LLM-based conversations",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# print(f"DEBUG: MONGO_URI = {settings.MONGO_URI}")
app.include_router(conversation.router)