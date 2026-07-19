from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound

from .models import Notification

User = get_user_model()


def get_notification_list(*, user: User) -> QuerySet[Notification]:
    """Retrieve all notifications for a user, newest first."""
    return Notification.objects.select_related("ticket").filter(user=user).order_by("-created_at")


def get_notification(notification_id: uuid.UUID, *, user: User) -> Notification:
    """Retrieve a single notification by ID for a specific user.

    Raises NotFound if the notification does not exist or belongs to another user.
    """
    try:
        return Notification.objects.select_related("ticket").get(id=notification_id, user=user)
    except Notification.DoesNotExist as err:
        raise NotFound("Notification not found.") from err
