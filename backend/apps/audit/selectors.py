from __future__ import annotations

import uuid

from django.db.models import QuerySet

from .models import TicketHistory


def get_ticket_history(ticket_id: uuid.UUID) -> QuerySet[TicketHistory]:
    """Retrieve history entries for a ticket, newest first."""
    return (
        TicketHistory.objects.select_related("changed_by")
        .filter(ticket_id=ticket_id)
        .order_by("-created_at")
    )
