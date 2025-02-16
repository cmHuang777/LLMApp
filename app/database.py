import os
import motor.motor_asyncio
from beanie import init_beanie
from app.config import settings
from app.models import Conversation, AuditLog

MONGO_DETAILS = settings.MONGO_URI

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    # Using the default database from the connection string
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[Conversation, AuditLog])
