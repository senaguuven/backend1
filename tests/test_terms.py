import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime, timedelta
from odmantic import ObjectId

from main import app  # FastAPI uygulaman
from users import schemas as user_schemas
from term import crud as term_crud
import config.auth


# 1. Admin mock kullanıcı objesi
def mock_admin_user() -> user_schemas.User:
    return user_schemas.User(
        id=ObjectId(),
        username="admin",
        user_email="admin@example.com",
        user_role=["admin"],
        user_name="Admin",
        user_surname="User",
        user_status=True,
        is_password_change_required=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# 2. TestClient fixture'ı
@pytest.fixture
def client():
    return TestClient(app)


# 3. Test için kullanılacak örnek term verisi
@pytest.fixture
def test_term_data():
    return {
        "term_name": "Test Term 2024",
        "term_start_date": datetime.now().isoformat(),
        "term_end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "term_students": []
    }


# 4. check_user dependency override factory
def override_check_user(roles=None):
    async def _override():
        return mock_admin_user()
    return _override


@pytest.mark.usefixtures("client", "test_term_data")
@pytest.mark.asyncio
async def test_create_term(mocker, client, test_term_data):
    # 5. Dependency override yapıyoruz (parantezsiz, çünkü factory dönüyor)
    app.dependency_overrides[config.auth.check_user] = override_check_user

    # 6. check_term_overlap fonksiyonunu mockla (çakışma yok varsayıyoruz)
    mocker.patch('term.crud.check_term_overlap', return_value=None)

    # 7. create_term fonksiyonunu mockla
    mock_created_term = term_crud.Term(**test_term_data)
    create_term_mock = mocker.patch('term.crud.create_term', return_value=mock_created_term)

    # 8. POST isteği yap
    response = client.post("/terms/", json=test_term_data)

    # 9. Override'ı kaldır (diğer testleri etkilememesi için)
    app.dependency_overrides = {}

    # 10. Assert'lar
    assert response.status_code == status.HTTP_201_CREATED

    # create_term fonksiyonunun doğru argümanla çağrıldığını kontrol et
    create_term_mock.assert_called_once()
    called_arg = create_term_mock.call_args[0][0]
    assert called_arg.term_name == test_term_data["term_name"]
    assert called_arg.term_start_date == test_term_data["term_start_date"]
    assert called_arg.term_end_date == test_term_data["term_end_date"]
    assert called_arg.term_students == test_term_data["term_students"]

    data = response.json()
    assert data["term_name"] == test_term_data["term_name"]
