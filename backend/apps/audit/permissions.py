from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class CanViewTicketHistory(BasePermission):
    """Allow access to ticket history based on role.

    ADMIN and MANAGER may view history for any ticket.
    AGENT may only view history for tickets assigned to them.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role in (User.Role.ADMIN, User.Role.MANAGER):
            return True

        return obj.assigned_to == user
