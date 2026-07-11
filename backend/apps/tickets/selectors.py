from __future__ import annotations

import uuid

from django.db.models import QuerySet

from .models import Ticket


def get_ticket(ticket_id: uuid.UUID) -> Ticket | None:
    """Retrieve a single ticket by ID."""
    try:
        return Ticket.objects.select_related("assigned_to", "created_by").get(id=ticket_id)
    except Ticket.DoesNotExist:
        return None


def get_ticket_list(
    *,
    filters: dict | None = None,
    search: str | None = None,
    ordering: str | None = None,
) -> QuerySet[Ticket]:
    """Retrieve a filtered, searchable, and sortable ticket queryset."""
    qs = Ticket.objects.select_related("assigned_to", "created_by").all()

    if filters:
        for field, value in filters.items():
            if value is not None and value != "":
                qs = qs.filter(**{field: value})

    if search:
        from django.db.models import Q

        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

    if ordering:
        qs = qs.order_by(ordering)

    return qs
