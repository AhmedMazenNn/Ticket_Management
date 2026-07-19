import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from .factories import AdminUserFactory, UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_user():
    return AdminUserFactory()


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


class TestLogin:
    def test_login_success(self, api_client, user):
        data = {"email": user.email, "password": "testpass123"}
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == user.email

    def test_login_invalid_credentials(self, api_client, user):
        data = {"email": user.email, "password": "wrongpassword"}
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Invalid credentials."

    def test_login_missing_fields(self, api_client):
        response = api_client.post("/api/auth/login/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, api_client):
        data = {"email": "nonexistent@example.com", "password": "testpass123"}
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRegister:
    def test_register_success(self, api_client):
        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"
        assert response.data["user"]["first_name"] == "New"
        assert response.data["user"]["last_name"] == "User"

    def test_register_duplicate_email(self, api_client, user):
        data = {"email": user.email, "password": "securepass123"}
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self, api_client):
        response = api_client.post("/api/auth/register/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        data = {"email": "short@example.com", "password": "123"}
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCurrentUser:
    def test_me_authenticated(self, auth_client, user):
        response = auth_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert response.data["first_name"] == user.first_name
        assert response.data["last_name"] == user.last_name
        assert response.data["role"] == user.role
        assert "password" not in response.data

    def test_me_unauthenticated(self, api_client):
        response = api_client.get("/api/auth/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_update_profile(self, auth_client, user):
        response = auth_client.patch(
            "/api/auth/me/", {"first_name": "Updated", "last_name": "Name"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"

    def test_me_update_email_rejected(self, auth_client, user):
        response = auth_client.patch("/api/auth/me/", {"email": "hacked@example.com"})
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email != "hacked@example.com"


class TestTokenRefresh:
    def test_token_refresh(self, api_client, user):
        login_response = api_client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
        )
        refresh_token = login_response.data["refresh"]

        response = api_client.post(
            "/api/auth/refresh/",
            {"refresh": refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_token_refresh_invalid(self, api_client):
        response = api_client.post(
            "/api/auth/refresh/",
            {"refresh": "invalid-token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    def test_logout(self, api_client, user):
        login_response = api_client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "testpass123"},
        )
        refresh_token = login_response.data["refresh"]

        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/auth/logout/",
            {"refresh": refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out."

    def test_logout_unauthenticated(self, api_client):
        response = api_client.post("/api/auth/logout/", {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_missing_refresh_token(self, auth_client):
        response = auth_client.post("/api/auth/logout/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Refresh token is required."


class TestUserList:
    def test_list_users_authenticated(self, auth_client, user):
        response = auth_client.get("/api/auth/users/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) >= 1

    def test_list_users_unauthenticated(self, api_client):
        response = api_client.get("/api/auth/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_excludes_inactive(self, auth_client):
        inactive = UserFactory(is_active=False)
        response = auth_client.get("/api/auth/users/")
        assert response.status_code == status.HTTP_200_OK
        user_ids = [u["id"] for u in response.data]
        assert str(inactive.id) not in user_ids


# ---------------------------------------------------------------------------
# Throttling — Login
# ---------------------------------------------------------------------------


class TestLoginThrottling:
    def test_login_succeeds_under_limit(self, api_client, user):
        from django.core.cache import cache

        cache.clear()
        data = {"email": user.email, "password": "testpass123"}
        for _ in range(10):
            response = api_client.post("/api/auth/login/", data)
            assert response.status_code == status.HTTP_200_OK

    def test_login_returns_429_after_limit(self, api_client, user):
        from django.core.cache import cache

        cache.clear()
        data = {"email": user.email, "password": "testpass123"}
        for _ in range(10):
            api_client.post("/api/auth/login/", data)
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_login_invalid_credentials_still_counts_toward_limit(self, api_client, user):
        from django.core.cache import cache

        cache.clear()
        data = {"email": user.email, "password": "wrongpassword"}
        for _ in range(10):
            api_client.post("/api/auth/login/", data)
        response = api_client.post("/api/auth/login/", data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Throttling — Register
# ---------------------------------------------------------------------------


class TestRegisterThrottling:
    def test_register_succeeds_under_limit(self, api_client):
        from django.core.cache import cache

        cache.clear()
        for i in range(5):
            data = {
                "email": f"newuser{i}@example.com",
                "password": "strongpass123",
                "first_name": "Test",
                "last_name": "User",
            }
            response = api_client.post("/api/auth/register/", data)
            assert response.status_code == status.HTTP_201_CREATED

    def test_register_returns_429_after_limit(self, api_client):
        from django.core.cache import cache

        cache.clear()
        for i in range(5):
            data = {
                "email": f"throttle{i}@example.com",
                "password": "strongpass123",
                "first_name": "Test",
                "last_name": "User",
            }
            api_client.post("/api/auth/register/", data)
        data = {
            "email": "overlimit@example.com",
            "password": "strongpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Throttling — Token Refresh
# ---------------------------------------------------------------------------


class TestTokenRefreshThrottling:
    def test_refresh_succeeds_under_limit(self, api_client, user):
        from django.core.cache import cache
        from rest_framework_simplejwt.tokens import RefreshToken

        cache.clear()
        refresh = str(RefreshToken.for_user(user))
        for _ in range(60):
            response = api_client.post("/api/auth/refresh/", {"refresh": refresh})
            assert response.status_code == status.HTTP_200_OK
            refresh = response.data["refresh"]

    def test_refresh_returns_429_after_limit(self, api_client, user):
        from django.core.cache import cache
        from rest_framework_simplejwt.tokens import RefreshToken

        cache.clear()
        refresh = str(RefreshToken.for_user(user))
        for _ in range(60):
            response = api_client.post("/api/auth/refresh/", {"refresh": refresh})
            refresh = response.data["refresh"]
        response = api_client.post("/api/auth/refresh/", {"refresh": refresh})
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ---------------------------------------------------------------------------
# Throttling — Change Password
# ---------------------------------------------------------------------------


class TestPasswordChangeThrottling:
    def test_password_change_succeeds_under_limit(self, auth_client):
        from django.core.cache import cache

        cache.clear()
        current_password = "testpass123"
        for _ in range(5):
            data = {"current_password": current_password, "new_password": "newpass123"}
            response = auth_client.post("/api/auth/change-password/", data)
            assert response.status_code == status.HTTP_200_OK
            current_password = "newpass123"

    def test_password_change_returns_429_after_limit(self, auth_client):
        from django.core.cache import cache

        cache.clear()
        current_password = "testpass123"
        for _ in range(5):
            data = {"current_password": current_password, "new_password": "newpass123"}
            auth_client.post("/api/auth/change-password/", data)
            current_password = "newpass123"
        data = {"current_password": current_password, "new_password": "anotherpass123"}
        response = auth_client.post("/api/auth/change-password/", data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
