# SQLAlchemy or Tortoise models
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .db import Base  # Import Base từ app/db.py

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    sent_messages = relationship("Message", back_populates="sender")
    received_messages = relationship("MessageRecipient", back_populates="recipient")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    subject = Column(String, nullable=True)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    sender = relationship("User", back_populates="sent_messages")
    recipients = relationship("MessageRecipient", back_populates="message")


class MessageRecipient(Base):
    __tablename__ = "message_recipients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    message = relationship("Message", back_populates="recipients")
    recipient = relationship("User", back_populates="received_messages")
