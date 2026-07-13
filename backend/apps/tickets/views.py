from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User

from .filters import TicketFilter
from .models import Ticket
from .permissions import CanCreateTicket, CanEditTicket
from .selectors import get_ticket, get_ticket_list
from .serializers import (
    TicketAgentUpdateSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketUpdateSerializer,
)
from .services import create_ticket, delete_ticket, update_ticket

DASHBOARD_STATS_TIMEOUT = 300  # 5 minutes


def _dashboard_cache_key(user):
    if user.role == User.Role.AGENT:
        return f"dashboard_stats_agent_{user.id}"
    return "dashboard_stats"


@extend_schema(tags=["Tickets"])
class TicketListCreateView(generics.ListCreateAPIView):
    """List tickets (scoped by role) or create a new ticket."""

    permission_classes = [IsAuthenticated, CanCreateTicket]
    filterset_class = TicketFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "priority"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TicketCreateSerializer
        return TicketListSerializer

    def get_queryset(self):
        return get_ticket_list(user=self.request.user)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = create_ticket(
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            priority=serializer.validated_data.get("priority", "MEDIUM"),
            status=serializer.validated_data.get("status", "OPEN"),
            assigned_to=serializer.validated_data.get("assigned_to"),
            created_by=request.user,
        )

        return Response(
            TicketDetailSerializer(ticket).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Tickets"])
class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a ticket."""

    permission_classes = [IsAuthenticated, CanEditTicket]
    lookup_field = "id"
    http_method_names = ["get", "put", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            if self.request.user.role == User.Role.AGENT:
                return TicketAgentUpdateSerializer
            return TicketUpdateSerializer
        return TicketDetailSerializer

    def get_object(self):
        ticket = get_ticket(self.kwargs["id"])
        if ticket is None:
            from rest_framework.exceptions import NotFound

            raise NotFound
        self.check_object_permissions(self.request, ticket)
        return ticket

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        ticket = self.get_object()

        if request.user.role == User.Role.AGENT:
            allowed_fields = {"status"}
            disallowed = set(request.data) - allowed_fields
            if disallowed:
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    dict.fromkeys(disallowed, "Agents may only update the status field.")
                )

        serializer = self.get_serializer(ticket, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_ticket = update_ticket(ticket, changed_by=request.user, **serializer.validated_data)

        return Response(TicketDetailSerializer(updated_ticket).data)

    def perform_destroy(self, instance):
        delete_ticket(instance)


@extend_schema(tags=["Tickets"])
class DashboardStatsView(APIView):
    """Return aggregate ticket statistics for the dashboard."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        cache_key = _dashboard_cache_key(request.user)
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        user = request.user
        if user.role == User.Role.AGENT:
            qs = Ticket.objects.filter(assigned_to=user)
        else:
            qs = Ticket.objects.all()

        total = qs.count()
        open_count = qs.filter(status=Ticket.Status.OPEN).count()
        in_progress = qs.filter(status=Ticket.Status.IN_PROGRESS).count()
        closed = qs.filter(status=Ticket.Status.CLOSED).count()

        recent = qs.select_related("assigned_to", "created_by").order_by("-created_at")[:5]

        response_data = {
            "total": total,
            "open": open_count,
            "in_progress": in_progress,
            "closed": closed,
            "recent_tickets": TicketListSerializer(recent, many=True).data,
            "priority_breakdown": {
                "low": qs.filter(priority=Ticket.Priority.LOW).count(),
                "medium": qs.filter(priority=Ticket.Priority.MEDIUM).count(),
                "high": qs.filter(priority=Ticket.Priority.HIGH).count(),
            },
        }
        cache.set(cache_key, response_data, timeout=DASHBOARD_STATS_TIMEOUT)
        return Response(response_data)


@extend_schema(tags=["Tickets"])
class MyStatsView(APIView):
    """Return ticket statistics scoped to the current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        cache_key = f"my_stats_{request.user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        assigned = Ticket.objects.filter(assigned_to=request.user)
        created = Ticket.objects.filter(created_by=request.user)

        response_data = {
            "assigned_total": assigned.count(),
            "assigned_open": assigned.filter(status=Ticket.Status.OPEN).count(),
            "assigned_in_progress": assigned.filter(status=Ticket.Status.IN_PROGRESS).count(),
            "assigned_closed": assigned.filter(status=Ticket.Status.CLOSED).count(),
            "created_total": created.count(),
            "assigned_tickets": TicketListSerializer(
                assigned.select_related("assigned_to", "created_by").order_by("-updated_at")[:10],
                many=True,
            ).data,
        }
        cache.set(cache_key, response_data, timeout=DASHBOARD_STATS_TIMEOUT)
        return Response(response_data)
