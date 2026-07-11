from __future__ import annotations

from django.contrib.auth import get_user_model

from .models import Ticket

User = get_user_model()


def create_ticket(
    *,
    title: str,
    description: str = "",
    priority: str = Ticket.Priority.MEDIUM,
    status: str = Ticket.Status.OPEN,
    assigned_to: User | None = None,
    created_by: User,
) -> Ticket:
    """Create a new ticket."""
    return Ticket.objects.create(
        title=title,
        description=description,
        priority=priority,
        status=status,
        assigned_to=assigned_to,
        created_by=created_by,
    )


def update_ticket(ticket: Ticket, **validated_data: dict) -> Ticket:
    """Update an existing ticket with the provided fields."""
    for field, value in validated_data.items():
        setattr(ticket, field, value)
    ticket.full_clean()
    ticket.save()
    return ticket


def delete_ticket(ticket: Ticket) -> None:
    """Delete a ticket."""
    ticket.delete()


def assign_ticket(ticket: Ticket, user: User | None) -> Ticket:
    """Assign or unassign a ticket."""
    ticket.assigned_to = user
    ticket.full_clean()
    ticket.save()
    return ticket
