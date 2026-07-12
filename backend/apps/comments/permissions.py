from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsAuthorOrAdmin(BasePermission):
    """Allow access only to the comment's author or an admin."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.role == User.Role.ADMIN
