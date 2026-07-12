from __future__ import annotations

import uuid

from django.db.models import QuerySet
from rest_framework.exceptions import NotFound

from apps.tickets.selectors import get_ticket

from .models import Comment


def get_comments_by_ticket(ticket_id: uuid.UUID) -> QuerySet[Comment]:
    """Retrieve all comments for a given ticket, newest first.

    Raises NotFound if the ticket does not exist.
    """
    ticket = get_ticket(ticket_id)
    if ticket is None:
        raise NotFound("Ticket not found.")
    return Comment.objects.select_related("author").filter(ticket=ticket)


def get_comment_by_id(comment_id: uuid.UUID) -> Comment:
    """Retrieve a single comment by ID.

    Raises NotFound if the comment does not exist.
    """
    try:
        return Comment.objects.select_related("author", "ticket").get(id=comment_id)
    except Comment.DoesNotExist as err:
        raise NotFound("Comment not found.") from err
