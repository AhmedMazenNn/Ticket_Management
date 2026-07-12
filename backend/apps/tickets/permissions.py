from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsAuthenticated(BasePermission):
    """Allow access only to authenticated users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanCreateTicket(BasePermission):
    """Only ADMIN and MANAGER may create tickets."""

    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        return request.user.role in (User.Role.ADMIN, User.Role.MANAGER)


class CanEditTicket(BasePermission):
    """Object-level permission for editing tickets.

    ADMIN and MANAGER may edit all fields on any ticket.
    AGENT may only update the status of tickets assigned to them.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role in (User.Role.ADMIN, User.Role.MANAGER):
            return True

        if request.method == "GET":
            return obj.assigned_to == user

        if request.method in ("PUT", "PATCH"):
            return obj.assigned_to == user

        return False
