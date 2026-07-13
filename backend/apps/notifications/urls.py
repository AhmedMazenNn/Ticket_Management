from django.urls import path

from .views import (
    NotificationDeleteView,
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
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
    path(
        "read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification_mark_all_read",
    ),
    path(
        "<uuid:id>/delete/",
        NotificationDeleteView.as_view(),
        name="notification_delete",
    ),
]
