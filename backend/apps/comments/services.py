from __future__ import annotations

from django.contrib.auth import get_user_model

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
    return Comment.objects.create(
        ticket=ticket,
        author=author,
        body=body,
    )


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
