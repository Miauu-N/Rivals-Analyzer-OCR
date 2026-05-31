import pytest
from fastapi import status

# List of endpoints to verify protection.
# Each entry is a tuple: (method, url, request_kwargs)
PROTECTED_ENDPOINTS = [
    ("GET", "/api/uploads/", {}),
    ("POST", "/api/uploads/upload-images", {}),
    ("GET", "/api/matches/", {}),
    ("DELETE", "/api/matches/clear", {}),
    ("GET", "/api/matches/recommended", {}),
    ("GET", "/api/matches/999", {}),  # Using a high ID to avoid conflicts, expects 404 if authenticated
    ("GET", "/api/analytics/summary", {}),
]

@pytest.fixture
def auth_headers(client):
    # Register and login a user to get auth headers
    email = "authuser@example.com"
    password = "password123"
    client.post(
        "/api/auth/register",
        json={"email": email, "password": password}
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": email, "password": password}
    )
    token_data = login_response.json()
    token = token_data["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.parametrize("method,url,kwargs", PROTECTED_ENDPOINTS)
def test_endpoints_require_authentication(client, method, url, kwargs):
    """Verifies that accessing protected endpoints without a token returns HTTP 401."""
    response = client.request(method, url, **kwargs)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.parametrize("method,url,kwargs", PROTECTED_ENDPOINTS)
def test_endpoints_allow_authenticated_access(client, auth_headers, method, url, kwargs):
    """Verifies that accessing protected endpoints with a valid token does not return HTTP 401."""
    # Add auth headers to request kwargs
    req_kwargs = kwargs.copy()
    req_kwargs["headers"] = auth_headers
    
    response = client.request(method, url, **req_kwargs)
    
    # We should NOT get 401 Unauthorized.
    # The actual response could be 200 (for empty lists), 404 (for missing match), or 422 (if payload is missing like files for upload).
    # But it must not be 401.
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
    
    # Let's verify specific expected responses when authenticated:
    if url == "/api/uploads/":
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    elif url == "/api/matches/":
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    elif url == "/api/matches/recommended":
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    elif url == "/api/matches/999":
        # Since the match does not exist, it should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Match not found"
    elif url == "/api/analytics/summary":
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "total_matches": 0,
            "win_rate": "0%",
            "avg_kda": "0.0",
            "top_heroes": []
        }
    elif url == "/api/uploads/upload-images":
        # Without files, FastAPI will return 422 Unprocessable Entity, which is correct because we passed authentication
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
