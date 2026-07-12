from django.urls import path

from .views import (
    NotificationDetailView,
    NotificationListView,
    NotificationMarkReadView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification_list"),
    path(
        "<uuid:id>/",
        NotificationDetailView.as_view(),
        name="notification_detail",
    ),
    path(
        "<uuid:id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification_mark_read",
    ),
]
