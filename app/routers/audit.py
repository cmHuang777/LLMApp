from fastapi import APIRouter
from typing import List
from app.models import AuditLog

router = APIRouter(prefix="/audits", tags=["audits"])

@router.get("/", response_model=List[AuditLog])
async def list_audits():
    audits = await AuditLog.find().to_list()
    return audits
