from django.contrib import admin

from .models import Ticket
from .services import _invalidate_ticket_caches


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "status",
        "priority",
        "assigned_to",
        "created_by",
        "created_at",
    ]
    list_filter = ["status", "priority"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        old_assignee_id = form.initial.get("assigned_to") if change else None
        super().save_model(request, obj, form, change)
        _invalidate_ticket_caches(
            creator_id=obj.created_by_id,
            assignee_id=obj.assigned_to_id,
            old_assignee_id=old_assignee_id,
        )

    def delete_model(self, request, obj):
        _invalidate_ticket_caches(
            creator_id=obj.created_by_id,
            assignee_id=obj.assigned_to_id,
        )
        super().delete_model(request, obj)
