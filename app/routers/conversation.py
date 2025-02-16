from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import Conversation, Message
from app.schemas import (
    ConversationCreate,
    ConversationResponse
)

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(conv_data: ConversationCreate):
    new_conv = Conversation(title=conv_data.title)
    await new_conv.insert()
    return await _build_conversation_response(new_conv)


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations():
    conversations = await Conversation.find().to_list()
    return [await _build_conversation_response(conv) for conv in conversations]


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    try:
        obj_id = PydanticObjectId(conversation_id)
    except:
        # If it's not a valid ObjectId, we just say "not found" (or 412, up to you)
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = await Conversation.get(obj_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return await _build_conversation_response(conv)

async def _build_conversation_response(conv: Conversation) -> ConversationResponse:
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        messages=[
            # Convert each message into the response schema
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp
            }
            for m in conv.messages
        ],
        created_at=conv.created_at,
        updated_at=conv.updated_at
    )