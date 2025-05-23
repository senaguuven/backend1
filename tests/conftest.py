import pytest
from fastapi.testclient import TestClient
from main import app

# Test için FastAPI test client fixture'ı
@pytest.fixture
def client():
    return TestClient(app)

# Mocking için pytest-mock fixture'ı (mocker)
# Bu fixture otomatik olarak pytest tarafından sağlanır, sadece import etmemiz yeterli.

# Ortak test verileri fixture'ları
@pytest.fixture
def test_user_data():
    return {
        "user_email": "test@example.com",
        "user_password": "testpassword123",
        "user_name": "Test",
        "user_surname": "User",
        "user_role": ["user"],
        "user_status": True,
        "is_password_change_required": True,
    }

@pytest.fixture
def admin_user_data():
    return {
        "user_email": "admin@example.com",
        "user_password": "adminpassword123",
        "user_name": "Admin",
        "user_surname": "User",
        "user_role": ["admin"],
        "user_status": True,
        "is_password_change_required": True,
    } 