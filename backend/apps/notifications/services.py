from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.tickets.models import Ticket

from .models import Notification

User = get_user_model()


def create_notification(
    *,
    ticket: Ticket,
    user: User,
    type: str,
) -> Notification:
    """Create an in-app notification.

    Args:
        ticket: The ticket this notification is about.
        user: The user who should receive this notification.
        type: One of Notification.Type values.

    Returns:
        The created Notification instance.
    """
    return Notification.objects.create(
        ticket=ticket,
        user=user,
        type=type,
    )
