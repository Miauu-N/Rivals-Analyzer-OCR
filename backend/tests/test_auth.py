import pytest
from fastapi import status
from app.models.user import User

def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "password_hash" not in data  # password_hash should not be returned in response

def test_register_user_duplicate_email(client):
    # Register first user
    client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    
    # Try to register user with same email again
    response = client.post(
        "/api/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

def test_register_user_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password123"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_user_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "shortpwd@example.com", "password": "short"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_user_success(client):
    # Register a user
    client.post(
        "/api/auth/register",
        json={"email": "loginuser@example.com", "password": "password123"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_incorrect_password(client):
    # Register a user
    client.post(
        "/api/auth/register",
        json={"email": "wrongpwd@example.com", "password": "password123"}
    )
    
    # Login with wrong password
    response = client.post(
        "/api/auth/login",
        data={"username": "wrongpwd@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Incorrect email or password"
