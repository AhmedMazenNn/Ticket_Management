from __future__ import annotations

from functools import partial

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.messaging.constants import RoutingKey
from apps.messaging.publisher import publish_event
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from apps.tickets.models import Ticket

from .models import Comment

User = get_user_model()


def create_comment(
    *,
    ticket: Ticket,
    author: User,
    body: str,
) -> Comment:
    """Create a new comment on a ticket."""
    comment = Comment.objects.create(
        ticket=ticket,
        author=author,
        body=body,
    )

    recipients = set()
    if ticket.created_by != author:
        recipients.add(ticket.created_by)
    if ticket.assigned_to and ticket.assigned_to != author:
        recipients.add(ticket.assigned_to)

    for user in recipients:
        create_notification(
            ticket=ticket,
            user=user,
            type=Notification.Type.COMMENT_ADDED,
            triggered_by=author,
        )

    transaction.on_commit(
        partial(
            publish_event,
            RoutingKey.COMMENT_CREATED,
            {
                "event": "comment.created",
                "comment_id": str(comment.id),
                "ticket_id": str(ticket.id),
                "author": str(author.id),
                "timestamp": comment.created_at.isoformat(),
            },
        )
    )

    return comment


def update_comment(comment: Comment, **validated_data: dict) -> Comment:
    """Update an existing comment with the provided fields."""
    for field, value in validated_data.items():
        setattr(comment, field, value)
    comment.full_clean()
    comment.save()
    return comment


def delete_comment(comment: Comment) -> None:
    """Delete a comment."""
    comment.delete()
