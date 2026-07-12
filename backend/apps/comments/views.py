from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.tickets.selectors import get_ticket

from .permissions import IsAuthorOrAdmin
from .selectors import get_comment_by_id, get_comments_by_ticket
from .serializers import CommentCreateSerializer, CommentDetailSerializer, CommentUpdateSerializer
from .services import create_comment, delete_comment, update_comment


@extend_schema(tags=["Comments"])
class CommentListCreateView(generics.ListCreateAPIView):
    """List all comments for a ticket, or create a new comment."""

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentDetailSerializer

    def get_queryset(self):
        return get_comments_by_ticket(self.kwargs["ticket_id"])

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = get_ticket(self.kwargs["ticket_id"])
        if ticket is None:
            from rest_framework.exceptions import NotFound

            raise NotFound("Ticket not found.")

        comment = create_comment(
            ticket=ticket,
            author=request.user,
            body=serializer.validated_data["body"],
        )

        return Response(
            CommentDetailSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Comments"])
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comment."""

    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]
    http_method_names = ["get", "put", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CommentUpdateSerializer
        return CommentDetailSerializer

    def get_object(self):
        return get_comment_by_id(self.kwargs["comment_id"])

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        comment = self.get_object()
        self.check_object_permissions(request, comment)

        serializer = self.get_serializer(comment, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_comment = update_comment(comment, **serializer.validated_data)

        return Response(CommentDetailSerializer(updated_comment).data)

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, instance)
        delete_comment(instance)
