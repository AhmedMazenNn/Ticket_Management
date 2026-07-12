from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.audit.services import create_history_entries

from .models import Ticket

User = get_user_model()

TRACKED_FIELDS = {"title", "description", "priority", "status", "assigned_to"}

PRIORITY_LABELS = {
    Ticket.Priority.LOW: "Low",
    Ticket.Priority.MEDIUM: "Medium",
    Ticket.Priority.HIGH: "High",
}

STATUS_LABELS = {
    Ticket.Status.OPEN: "Open",
    Ticket.Status.IN_PROGRESS: "In Progress",
    Ticket.Status.CLOSED: "Closed",
}


def _format_value(field_name: str, value) -> str | None:
    """Format a ticket field value to a human-readable string."""
    if value is None:
        return None
    if field_name == "priority":
        return PRIORITY_LABELS.get(value, str(value))
    if field_name == "status":
        return STATUS_LABELS.get(value, str(value))
    if field_name == "assigned_to":
        return value.email if hasattr(value, "email") else str(value)
    return str(value)


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
    ticket = Ticket.objects.create(
        title=title,
        description=description,
        priority=priority,
        status=status,
        assigned_to=assigned_to,
        created_by=created_by,
    )
    create_history_entries(
        ticket=ticket,
        changed_by=created_by,
        changes=[("created", None, "Ticket created")],
    )
    return ticket


def update_ticket(ticket: Ticket, *, changed_by: User, **validated_data: dict) -> Ticket:
    """Update an existing ticket with the provided fields."""
    changes = []
    for field, new_value in validated_data.items():
        if field not in TRACKED_FIELDS:
            continue
        old_value = getattr(ticket, field)
        if old_value != new_value:
            changes.append(
                (field, _format_value(field, old_value), _format_value(field, new_value))
            )

    for field, value in validated_data.items():
        setattr(ticket, field, value)
    ticket.full_clean()
    ticket.save()

    if changes:
        create_history_entries(
            ticket=ticket,
            changed_by=changed_by,
            changes=changes,
        )

    return ticket


def delete_ticket(ticket: Ticket) -> None:
    """Delete a ticket."""
    ticket.delete()


def assign_ticket(ticket: Ticket, user: User | None, *, changed_by: User) -> Ticket:
    """Assign or unassign a ticket."""
    old_assignee = ticket.assigned_to
    if old_assignee != user:
        ticket.assigned_to = user
        ticket.full_clean()
        ticket.save()
        create_history_entries(
            ticket=ticket,
            changed_by=changed_by,
            changes=[
                (
                    "assigned_to",
                    _format_value("assigned_to", old_assignee),
                    _format_value("assigned_to", user),
                )
            ],
        )
    return ticket
