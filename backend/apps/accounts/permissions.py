from rest_framework.permissions import BasePermission

from .models import User


class IsAuthenticated(BasePermission):
    """Allow access only to authenticated users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN
        )
