from __future__ import annotations

from functools import partial

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction

from apps.audit.services import create_history_entries
from apps.messaging.constants import RoutingKey
from apps.messaging.publisher import publish_event
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


def _invalidate_ticket_caches(*, creator_id, assignee_id=None, old_assignee_id=None):
    """Invalidate dashboard cache keys after ticket mutations."""
    cache.delete("dashboard_stats")
    cache.delete(f"dashboard_stats_agent_{creator_id}")
    cache.delete(f"my_stats_{creator_id}")
    if assignee_id and assignee_id != creator_id:
        cache.delete(f"dashboard_stats_agent_{assignee_id}")
        cache.delete(f"my_stats_{assignee_id}")
    if old_assignee_id and old_assignee_id != creator_id and old_assignee_id != assignee_id:
        cache.delete(f"dashboard_stats_agent_{old_assignee_id}")
        cache.delete(f"my_stats_{old_assignee_id}")


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
            triggered_by=created_by,
        )
    _invalidate_ticket_caches(
        creator_id=created_by.id,
        assignee_id=assigned_to.id if assigned_to else None,
    )
    transaction.on_commit(
        partial(
            publish_event,
            RoutingKey.TICKET_CREATED,
            {
                "event": "ticket.created",
                "ticket_id": str(ticket.id),
                "title": ticket.title,
                "created_by": str(created_by.id),
                "timestamp": ticket.created_at.isoformat(),
            },
        )
    )
    return ticket


def update_ticket(ticket: Ticket, *, changed_by: User, **validated_data: dict) -> Ticket:
    """Update an existing ticket with the provided fields."""
    old_assignee_id = ticket.assigned_to_id
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
        _notify_ticket_update(ticket=ticket, changed_by=changed_by, changes=changes)
        _invalidate_ticket_caches(
            creator_id=ticket.created_by_id,
            assignee_id=ticket.assigned_to_id,
            old_assignee_id=old_assignee_id,
        )
        changed_fields = {field for field, _, _ in changes}
        if "status" in changed_fields:
            routing_key = RoutingKey.TICKET_STATUS_CHANGED
            event = "ticket.status_changed"
        elif "priority" in changed_fields:
            routing_key = RoutingKey.TICKET_PRIORITY_CHANGED
            event = "ticket.priority_changed"
        elif "assigned_to" in changed_fields:
            routing_key = RoutingKey.TICKET_ASSIGNED
            event = "ticket.assigned"
        else:
            routing_key = RoutingKey.TICKET_UPDATED
            event = "ticket.updated"
        transaction.on_commit(
            partial(
                publish_event,
                routing_key,
                {
                    "event": event,
                    "ticket_id": str(ticket.id),
                    "changed_by": str(changed_by.id),
                    "changes": [{"field": f, "old": o, "new": n} for f, o, n in changes],
                    "timestamp": ticket.updated_at.isoformat(),
                },
            )
        )

    return ticket


def delete_ticket(ticket: Ticket) -> None:
    """Delete a ticket."""
    _invalidate_ticket_caches(
        creator_id=ticket.created_by_id,
        assignee_id=ticket.assigned_to_id,
    )
    ticket.delete()


def _notify_ticket_update(*, ticket: Ticket, changed_by: User, changes: list[tuple]) -> None:
    """Create notifications based on which fields actually changed.

    Args:
        ticket: The updated ticket.
        changed_by: The user who made the change.
        changes: List of (field_name, old_value, new_value) tuples.
    """
    changed_fields = {field for field, _, _ in changes}
    recipients: dict[str, set[User]] = {}

    if "assigned_to" in changed_fields and ticket.assigned_to:
        recipients.setdefault(Notification.Type.TICKET_ASSIGNED, set()).add(ticket.assigned_to)

    if "status" in changed_fields:
        recipients.setdefault(Notification.Type.STATUS_CHANGED, set()).add(ticket.created_by)
        if ticket.assigned_to:
            recipients[Notification.Type.STATUS_CHANGED].add(ticket.assigned_to)

    if "priority" in changed_fields:
        recipients.setdefault(Notification.Type.PRIORITY_CHANGED, set()).add(ticket.created_by)
        if ticket.assigned_to:
            recipients[Notification.Type.PRIORITY_CHANGED].add(ticket.assigned_to)

    other_fields = {"title", "description"}
    if other_fields & changed_fields:
        if ticket.created_by != changed_by:
            recipients.setdefault(Notification.Type.TICKET_UPDATED, set()).add(ticket.created_by)
        if ticket.assigned_to and ticket.assigned_to != changed_by:
            recipients.setdefault(Notification.Type.TICKET_UPDATED, set()).add(ticket.assigned_to)

    for notif_type, users in recipients.items():
        for user in users:
            if user != changed_by:
                create_notification(
                    ticket=ticket,
                    user=user,
                    type=notif_type,
                    triggered_by=changed_by,
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
                triggered_by=changed_by,
            )
        affected_ids = {changed_by.id, ticket.created_by_id}
        if old_assignee:
            affected_ids.add(old_assignee.id)
        if user:
            affected_ids.add(user.id)
        cache.delete("dashboard_stats")
        for uid in affected_ids:
            cache.delete(f"dashboard_stats_agent_{uid}")
            cache.delete(f"my_stats_{uid}")
        transaction.on_commit(
            partial(
                publish_event,
                RoutingKey.TICKET_ASSIGNED,
                {
                    "event": "ticket.assigned",
                    "ticket_id": str(ticket.id),
                    "changed_by": str(changed_by.id),
                    "assigned_to": str(user.id) if user else None,
                    "timestamp": ticket.updated_at.isoformat(),
                },
            )
        )
    return ticket
