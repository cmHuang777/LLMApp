from enum import Enum
from beanie import Document
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(BaseModel):
    role: RoleEnum
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(Document):
    conversation_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "conversations"

    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at=datetime.now(timezone.utc)

class AuditLog(Document):
    og_id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: Optional[str]
    prompt: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "audit_logs"
