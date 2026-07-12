from django.urls import path

from .views import CommentDetailView

urlpatterns = [
    path(
        "<uuid:comment_id>/",
        CommentDetailView.as_view(),
        name="comment_detail",
    ),
]
