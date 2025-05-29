# FastAPI routes
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from . import models, schemas
from .db import get_db

# Khởi tạo APIRouter chính cho tất cả các API
api_router = APIRouter()

# =====================================================================
# API NGƯỜI DÙNG (USER API)
# =====================================================================

@api_router.post(
    "/users/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Tạo một người dùng mới trong hệ thống.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user_id = uuid.uuid4()
    db_user = models.User(id=new_user_id, email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@api_router.get("/users/", response_model=List[schemas.User], tags=["users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Liệt kê tất cả người dùng trong hệ thống.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@api_router.get("/users/{user_id}", response_model=schemas.User, tags=["users"])
def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết của một người dùng theo ID.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user


# =====================================================================
# API TIN NHẮN (MESSAGE API)
# =====================================================================


@api_router.post(
    "/messages/",
    response_model=schemas.Message,
    status_code=status.HTTP_201_CREATED,
    tags=["messages"],
)
async def create_message(
    message_data: schemas.MessageCreate, db: Session = Depends(get_db)
):
    """
    Gửi tin nhắn cho một hoặc nhiều người nhận.
    """
    # Kiểm tra người gửi có tồn tại không
    sender = (
        db.query(models.User).filter(models.User.id == message_data.sender_id).first()
    )
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found.")

    # Tạo tin nhắn
    new_message_id = uuid.uuid4()
    db_message = models.Message(
        id=new_message_id,
        sender_id=message_data.sender_id,
        subject=message_data.subject,
        content=message_data.content,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(db_message)

    # Tạo các bản ghi người nhận cho tin nhắn
    if not message_data.recipient_ids:
        raise HTTPException(
            status_code=400, detail="Message must have at least one recipient."
        )

    for recipient_id in message_data.recipient_ids:
        db_recipient_user = (
            db.query(models.User).filter(models.User.id == recipient_id).first()
        )
        if not db_recipient_user:
            # Rollback transaction if any recipient is not found
            db.rollback()
            raise HTTPException(
                status_code=404, detail=f"Recipient with ID {recipient_id} not found."
            )

        db_msg_recipient = models.MessageRecipient(
            message_id=new_message_id, recipient_id=recipient_id
        )
        db.add(db_msg_recipient)

    db.commit()
    db.refresh(db_message)
    return db_message


@api_router.get(
    "/messages/{message_id}", response_model=schemas.Message, tags=["messages"]
)
def read_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết của một tin nhắn theo ID.
    """
    db_message = (
        db.query(models.Message).filter(models.Message.id == message_id).first()
    )
    if db_message is None:
        raise HTTPException(status_code=404, detail="Messages not found")

    return db_message


@api_router.patch(
    "/messages/recipients/{recipient_entry_id}/read",
    response_model=schemas.MessageRecipient,
    tags=["messages"],
)
def mark_message_as_read(recipient_entry_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Đánh dấu một tin nhắn cụ thể (được nhận bởi một người dùng cụ thể) là đã đọc.
    """
    db_recipient_entry = (
        db.query(models.MessageRecipient)
        .filter(models.MessageRecipient.id == recipient_entry_id)
        .first()
    )

    if db_recipient_entry is None:
        raise HTTPException(status_code=404, detail="Message recipient entry not found")

    if not db_recipient_entry.read:  # Chỉ cập nhật nếu chưa đọc
        db_recipient_entry.read = True
        db_recipient_entry.read_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add(db_recipient_entry)
        db.commit()
        db.refresh(db_recipient_entry)

    return db_recipient_entry


@api_router.get(
    "/users/{user_id}/sent_messages",
    response_model=List[schemas.Message],
    tags=["messages", "users"],
)
def get_sent_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Xem danh sách tất cả các tin nhắn mà một người dùng đã gửi.
    """
    # Kiểm tra user_id có tồn tại không
    user_exists = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found.")

    # Tải tin nhắn đã gửi. Sử dụng eager loading (joinedload) để tải thông tin người gửi cùng lúc.
    # Note: 'sender' relationship on Message is for linking to User, not the other way around.
    # So we just query messages filtering by sender_id.
    messages = (
        db.query(models.Message).filter(models.Message.sender_id == user_id).all()
    )
    return messages


@api_router.get(
    "/users/{user_id}/inbox",
    response_model=List[schemas.MessageInboxItem],
    tags=["messages", "users"],
)
def get_inbox_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Xem tất cả tin nhắn trong hộp thư đến của một người dùng.
    Bao gồm cả tin nhắn đã đọc và chưa đọc.
    """
    # Kiểm tra user_id có tồn tại không
    user_exists = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found.")

    # Truy vấn tin nhắn trong hộp thư đến
    # Sử dụng joinedload để tải thông tin người gửi (Message.sender) và bản ghi người nhận (MessageRecipient)
    # Tải thông tin người gửi và trạng thái đọc của tin nhắn
    inbox_entries = (
        db.query(models.Message, models.MessageRecipient)
        .join(
            models.MessageRecipient,
            models.Message.id == models.MessageRecipient.message_id,
        )
        .options(joinedload(models.Message.sender))
        .filter(
            models.MessageRecipient.recipient_id
            == user_id  # Eager load the sender information
        )
        .all()
    )

    # Chuyển đổi kết quả sang định dạng MessageInboxItem
    result = []
    for message, recipient_entry in inbox_entries:
        #  Kiểm tra xem message.sender có phải là None không trước khi tạo schemas.User
        sender_schema = (
            schemas.User.model_validate(message.sender) if message.sender else None
        )

        result.append(
            schemas.MessageInboxItem(
                id=message.id,
                sender_id=message.sender_id,
                subject=message.subject,
                content=message.content,
                timestamp=message.timestamp,
                recipient_entry_id=recipient_entry.id,
                read=recipient_entry.read,
                read_at=recipient_entry.read_at,
                sender=sender_schema,
            )
        )

        return result


@api_router.get(
    "/users/{user_id}/inbox/unread",
    response_model=List[schemas.MessageInboxItem],
    tags=["messages", "users"],
)
def get_unread_inbox_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Xem tất cả tin nhắn chưa đọc trong hộp thư đến của một người dùng.
    """
    # Kiểm tra user_id có tồn tại không
    user_exists = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found.")

    inbox_entries = (
        db.query(models.Message, models.MessageRecipient)
        .join(
            models.MessageRecipient,
            models.Message.id == models.MessageRecipient.message_id,
        )
        .options(joinedload(models.Message.sender))
        .filter(
            models.MessageRecipient.recipient_id == user_id,
            models.MessageRecipient.read == False,
        )
        .all()
    )

    result = []
    for message, recipient_entry in inbox_entries:
        sender_schema = (
            schemas.User.model_validate(message.sender) if message.sender else None
        )
        result.append(
            schemas.MessageInboxItem(
                id=message.id,
                sender_id=message.sender_id,
                subject=message.subject,
                content=message.content,
                timestamp=message.timestamp,
                recipient_entry_id=recipient_entry.id,
                read=recipient_entry.read,
                read_at=recipient_entry.read_at,
                sender=sender_schema,
            )
        )

    return result


@api_router.get("/messages/{message_id}/recipients", tags=["messages"])
def get_message_recipient(message_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Xem tất cả người nhận của một tin nhắn cụ thể và trạng thái đọc của họ.
    """
    # Kiểm tra message_id có tồn tại không
    message_exists = (
        db.query(models.Message).filter(models.Message.id == message_id).first()
    )
    if not message_exists:
        raise HTTPException(status_code=404, detail="Message not found.")

    # Lấy thông tin người nhận và join với bảng User để lấy tên/email
    recipient_data = (
        db.query(models.MessageRecipient, models.User)
        .join(models.User, models.MessageRecipient.recipient_id == models.User.id)
        .filter(models.MessageRecipient.message_id == message_id)
        .all()
    )

    # Format kết quả
    result = []
    for recipient_entry, user in recipient_data:
        result.append(
            {
                "recipient_entry_id": recipient_entry.id,
                "recipient_id": user.id,
                "recipient_name": user.name,
                "recipient_email": user.email,
                "read": recipient_entry.read,
                "read_at": recipient_entry.read_at,
            }
        )

    return result
