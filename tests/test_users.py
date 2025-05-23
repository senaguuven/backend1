import pytest
from fastapi import status
from users import crud as user_crud
from main import app

# Admin olarak login olup token almak için yardımcı fonksiyon
def get_admin_auth_token(client, admin_user):
    # Admin kullanıcısını oluştur (eğer yoksa - testler birbirinden bağımsız olmalı)
    # Normalde test fixture'ları bu hazırlığı yapmalı, ama test client ile yapıyorsak...
    # Basitlik için, testin başında admin kullanıcı oluşturmayı tekrarlayalım.
    client.post("/users/", json=admin_user) # Bu adımın başarılı olduğu varsayılıyor (mocked db ile)
    
    login_data = {
        "username": admin_user["user_email"],
        "password": admin_user["user_password"]
    }
    login_response = client.post("/users/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK # Login başarılı olmalı
    return login_response.json()["access_token"]

def test_create_user(client, mock_db, test_user, admin_user):
    # Admin olarak login olup token al
    admin_token = get_admin_auth_token(client, admin_user)
    
    # Kullanıcı oluşturma isteğini admin token ile gönder
    response = client.post(
        "/users/", 
        json=test_user,
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_email"] == test_user["user_email"]
    assert data["user_name"] == test_user["user_name"]
    assert "user_password" not in data

def test_login_user(client, mock_db, test_user):
    # Önce kullanıcıyı oluştur
    client.post("/users/", json=test_user)
    
    # Login denemesi
    login_data = {
        "username": test_user["user_email"],
        "password": test_user["user_password"]
    }
    response = client.post("/users/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_users_unauthorized(client, mock_db):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_users_authorized(client, mock_db, admin_user):
    # Admin olarak login olup token al
    admin_token = get_admin_auth_token(client, admin_user)
    
    # Kullanıcıları listeleme isteğini admin token ile gönder
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list) 