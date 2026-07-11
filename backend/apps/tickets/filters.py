import django_filters

from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    assigned_to = django_filters.UUIDFilter(field_name="assigned_to__id", lookup_expr="exact")
    created_by = django_filters.UUIDFilter(field_name="created_by__id", lookup_expr="exact")

    class Meta:
        model = Ticket
        fields = ["status", "priority", "assigned_to", "created_by"]
