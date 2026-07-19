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
    triggered_by: User | None = None,
) -> Notification:
    """Create an in-app notification and enqueue email.

    Args:
        ticket: The ticket this notification is about.
        user: The user who should receive this notification.
        type: One of Notification.Type values.
        triggered_by: The user who caused this notification.

    Returns:
        the created Notification instance.
    """
    notification = Notification.objects.create(
        ticket=ticket,
        user=user,
        type=type,
    )

    send_notification_email.delay(
        notification_id=str(notification.id),
        recipient_name=user.first_name or user.email.split("@")[0],
        recipient_email=user.email,
        notification_type=type,
        ticket_id=str(ticket.id),
        ticket_title=ticket.title,
        ticket_priority=ticket.priority,
        ticket_status=ticket.status,
        triggered_by_name=(
            f"{triggered_by.first_name} {triggered_by.last_name}".strip() if triggered_by else ""
        ),
        description=ticket.description[:300] if ticket.description else "",
    )

    return notification
