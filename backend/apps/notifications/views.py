from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .permissions import IsNotificationOwner
from .selectors import get_notification, get_notification_list
from .serializers import NotificationSerializer


@extend_schema(tags=["Notifications"])
class NotificationListView(generics.ListAPIView):
    """List notifications for the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = get_notification_list(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() in ("true", "1", "yes"))
        return qs


@extend_schema(tags=["Notifications"])
class NotificationDetailView(generics.RetrieveAPIView):
    """Retrieve a single notification."""

    permission_classes = [IsAuthenticated, IsNotificationOwner]
    serializer_class = NotificationSerializer
    lookup_field = "id"

    def get_object(self):
        return get_notification(self.kwargs["id"], user=self.request.user)


@extend_schema(tags=["Notifications"])
class NotificationMarkReadView(generics.GenericAPIView):
    """Mark a notification as read."""

    permission_classes = [IsAuthenticated, IsNotificationOwner]
    serializer_class = NotificationSerializer

    def patch(self, request: Request, *args, **kwargs) -> Response:
        notification = get_notification(self.kwargs["id"], user=request.user)
        self.check_object_permissions(request, notification)
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)
