from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate


def list_messages(db: Session, limit: int = 100) -> list[Message]:
    stmt = select(Message).order_by(Message.id.desc()).limit(limit)
    return list(reversed(db.scalars(stmt).all()))


def create_message(db: Session, data: MessageCreate) -> Message:
    message = Message(role="user", content=data.content)
    db.add(message)
    db.commit()
    return message
