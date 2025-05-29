# Pydantic models
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Message Schemas ---
class MessageBase(BaseModel):
    sender_id: uuid.UUID
    subject: Optional[str] = None
    content: str


class MessageCreate(MessageBase):
    recipient_ids: List[uuid.UUID]


class Message(MessageBase):
    id: uuid.UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Message Recipient Schemas ---
class MessageRecipientBase(BaseModel):
    message_id: uuid.UUID
    recipient_id: uuid.UUID
    read: bool = False


class MessageRecipientCreate(MessageRecipientBase):
    pass


class MessageRecipient(MessageRecipientBase):
    id: uuid.UUID
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Message Detail Schemas ---


class MessageDetail(Message):
    sender: User  # Eager loaded User object for the sender
    recipients: List[MessageRecipient]  # List of recipient entries

    model_config = ConfigDict(from_attributes=True)


# Schema cho các mục trong hộp thư đến (inbox)
class MessageInboxItem(Message):
    recipient_entry_id: uuid.UUID  # ID của bản ghi MessageRecipient
    read: bool
    read_at: Optional[datetime]
    sender: User  # Thông tin người gửi của tin nhắn

    model_config = ConfigDict(from_attributes=True)
