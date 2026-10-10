from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.message import MessageCreate, MessageRead
from app.services import message_service

router = APIRouter(prefix="/messages", tags=["messages"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[MessageRead])
def list_messages(db: DbSession):
    return message_service.list_messages(db)


@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(payload: MessageCreate, db: DbSession):
    return message_service.create_message(db, payload)
