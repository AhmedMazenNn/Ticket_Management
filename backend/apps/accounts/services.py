from django.contrib.auth import authenticate

from .models import User


def authenticate_user(email: str, password: str) -> User | None:
    """Authenticate a user by email and password."""
    return authenticate(username=email, password=password)
