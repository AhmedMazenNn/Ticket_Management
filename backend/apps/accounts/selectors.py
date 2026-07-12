from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_email(email: str) -> User | None:
    """Retrieve a user by email address."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
