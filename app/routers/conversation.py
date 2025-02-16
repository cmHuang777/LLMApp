from datetime import datetime, timezone
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import Conversation, Message
from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate
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
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = await Conversation.get(obj_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return await _build_conversation_response(conv)

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: str, conv_update: ConversationUpdate):
    try:
        obj_id = PydanticObjectId(conversation_id)
    except:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = await Conversation.get(obj_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conv_update.title is not None:
        conv.title = conv_update.title

    conv.updated_at = datetime.now(timezone.utc)
    await conv.save()
    return await _build_conversation_response(conv)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str):
    try:
        obj_id = PydanticObjectId(conversation_id)
    except:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv = await Conversation.get(obj_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await conv.delete()
    return


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