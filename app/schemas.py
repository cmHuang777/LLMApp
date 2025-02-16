from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models import RoleEnum

class MessageCreate(BaseModel):
    role: RoleEnum
    content: str

class ConversationCreate(BaseModel):
    title: str

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class MessageResponse(BaseModel):
    role: RoleEnum
    content: str
    timestamp: datetime

class ConversationResponse(BaseModel):
    id: str
    title: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime