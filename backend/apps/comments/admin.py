from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "ticket",
        "author",
        "body",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["body"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
