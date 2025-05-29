# Test user-related functionality
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import uuid

# Import các thành phần từ ứng dụng của bạn
from app.main import app
from app.db import Base, get_db
from app.models import User

# Cấu hình một database riêng biệt cho việc test (SQLite in-memory)
# Điều này giúp các test chạy nhanh và độc lập mà không ảnh hưởng đến DB phát triển
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(name="session")
def session_fixture():
    # Tạo tất cả các bảng trong test database trước mỗi test
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Xóa tất cả các bảng sau mỗi test để đảm bảo môi trường sạch
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Ghi đè dependency get_db để sử dụng session của test database
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as client:
        yield client
    # Xóa ghi đè dependency sau khi test hoàn tất
    app.dependency_overrides.clear()

# =====================================================================
# TESTS CHO API NGƯỜI DÙNG
# =====================================================================

def test_client_user(client: TestClient, session: Session):
    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "created_at" in data
    assert session.query(User).filter(User.email == "test@example.com").first() is not None

def test_create_user_duplicate_email(client: TestClient):
    client.post("/api/v1/users/", json={"email": "duplicate@example.com", "name": "User One"})
    response = client.post("/api/v1/users/", json={"email": "duplicate@example.com", "name": "User Two"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_read_users_empty(client: TestClient):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_users_with_data(client: TestClient, session: Session):
    user1 = User(id=uuid.uuid4(), email="user1@example.com", name="User One")
    user2 = User(id=uuid.uuid4(), email="user2@example.com", name="User Two")
    session.add_all([user1, user2])
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(user["email"] == "user1@example.com" for user in data)
    assert any(user["email"] == "user2@example.com" for user in data)

def test_read_user_by_id(client: TestClient, session: Session):
    test_user_id = uuid.uuid4()
    test_user = User(id=test_user_id, email="specific@example.com", name="Specific User")
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    response = client.get(f"/api/v1/users/{test_user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user_id)
    assert data["email"] == "specific@example.com"
    assert data["name"] == "Specific User"

def test_read_user_not_found(client: TestClient):
    non_existent_id = uuid.uuid4()
    response = client.get(f"/api/v1/users/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."