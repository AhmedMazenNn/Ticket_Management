from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """Allow access only to authenticated users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsNotificationOwner(BasePermission):
    """Allow access only to the notification's recipient."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
