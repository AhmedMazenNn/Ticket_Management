from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tickets.selectors import get_ticket

from .permissions import CanViewTicketHistory
from .selectors import get_ticket_history
from .serializers import TicketHistorySerializer


@extend_schema(tags=["Tickets"])
class TicketHistoryView(generics.ListAPIView):
    """List history entries for a ticket."""

    permission_classes = [IsAuthenticated, CanViewTicketHistory]
    serializer_class = TicketHistorySerializer
    pagination_class = None

    def get_queryset(self):
        return get_ticket_history(self.kwargs["ticket_id"])

    def list(self, request: Request, *args, **kwargs) -> Response:
        ticket = get_ticket(self.kwargs["ticket_id"])
        if ticket is None:
            from rest_framework.exceptions import NotFound

            raise NotFound("Ticket not found.")
        self.check_object_permissions(request, ticket)
        return super().list(request, *args, **kwargs)
