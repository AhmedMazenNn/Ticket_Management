from django.urls import path

from apps.audit.views import TicketHistoryView
from apps.comments.views import CommentListCreateView

from .views import (
    DashboardStatsView,
    MyStatsView,
    TicketDetailView,
    TicketListCreateView,
)

urlpatterns = [
    path("", TicketListCreateView.as_view(), name="ticket_list_create"),
    path("dashboard_stats/", DashboardStatsView.as_view(), name="dashboard_stats"),
    path("my_stats/", MyStatsView.as_view(), name="my_stats"),
    path("<uuid:id>/", TicketDetailView.as_view(), name="ticket_detail"),
    path(
        "<uuid:ticket_id>/comments/",
        CommentListCreateView.as_view(),
        name="ticket_comments",
    ),
    path(
        "<uuid:ticket_id>/history/",
        TicketHistoryView.as_view(),
        name="ticket_history",
    ),
]
