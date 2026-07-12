from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.audit.services import create_history_entries
from apps.notifications.models import Notification
from apps.notifications.services import create_notification

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
    if assigned_to and assigned_to != created_by:
        create_notification(
            ticket=ticket,
            user=assigned_to,
            type=Notification.Type.TICKET_ASSIGNED,
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
        _notify_ticket_update(ticket=ticket, changed_by=changed_by, validated_data=validated_data)

    return ticket


def delete_ticket(ticket: Ticket) -> None:
    """Delete a ticket."""
    ticket.delete()


def _notify_ticket_update(
    *, ticket: Ticket, changed_by: User, validated_data: dict
) -> None:
    """Create notifications based on which fields changed."""
    recipients: dict[str, set[User]] = {}

    if "assigned_to" in validated_data and ticket.assigned_to:
        recipients.setdefault(Notification.Type.TICKET_ASSIGNED, set()).add(
            ticket.assigned_to
        )

    if "status" in validated_data:
        recipients.setdefault(Notification.Type.STATUS_CHANGED, set()).add(
            ticket.created_by
        )
        if ticket.assigned_to:
            recipients[Notification.Type.STATUS_CHANGED].add(ticket.assigned_to)

    if "priority" in validated_data:
        recipients.setdefault(Notification.Type.PRIORITY_CHANGED, set()).add(
            ticket.created_by
        )
        if ticket.assigned_to:
            recipients[Notification.Type.PRIORITY_CHANGED].add(ticket.assigned_to)

    other_fields = {"title", "description"}
    if other_fields & validated_data.keys():
        if ticket.created_by != changed_by:
            recipients.setdefault(Notification.Type.TICKET_UPDATED, set()).add(
                ticket.created_by
            )
        if ticket.assigned_to and ticket.assigned_to != changed_by:
            recipients.setdefault(Notification.Type.TICKET_UPDATED, set()).add(
                ticket.assigned_to
            )

    for notif_type, users in recipients.items():
        for user in users:
            if user != changed_by:
                create_notification(
                    ticket=ticket,
                    user=user,
                    type=notif_type,
                )


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
        if user and user != changed_by:
            create_notification(
                ticket=ticket,
                user=user,
                type=Notification.Type.TICKET_ASSIGNED,
            )
    return ticket
