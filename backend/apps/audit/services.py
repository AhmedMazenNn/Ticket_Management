from __future__ import annotations

from django.contrib.auth import get_user_model

from .models import TicketHistory

User = get_user_model()


def create_history_entries(
    *,
    ticket,
    changed_by: User,
    changes: list[tuple[str, str | None, str | None]],
) -> list[TicketHistory]:
    """Create history entries for a ticket.

    Args:
        ticket: The Ticket instance that changed.
        changed_by: The user who made the change.
        changes: List of (field_name, old_value, new_value) tuples.

    Returns:
        List of created TicketHistory instances.
    """
    entries = [
        TicketHistory(
            ticket=ticket,
            changed_by=changed_by,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
        )
        for field_name, old_value, new_value in changes
    ]
    return TicketHistory.objects.bulk_create(entries)
