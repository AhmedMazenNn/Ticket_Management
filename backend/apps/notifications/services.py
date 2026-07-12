from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.tickets.models import Ticket

from .models import Notification
from .tasks import send_notification_email

User = get_user_model()


def create_notification(
    *,
    ticket: Ticket,
    user: User,
    type: str,
) -> Notification:
    """Create an in-app notification and enqueue email.

    Args:
        ticket: The ticket this notification is about.
        user: The user who should receive this notification.
        type: One of Notification.Type values.

    Returns:
        The created Notification instance.
    """
    notification = Notification.objects.create(
        ticket=ticket,
        user=user,
        type=type,
    )

    send_notification_email.delay(
        notification_id=str(notification.id),
        recipient_email=user.email,
        notification_type=type,
        ticket_id=str(ticket.id),
        ticket_title=ticket.title,
    )

    return notification
