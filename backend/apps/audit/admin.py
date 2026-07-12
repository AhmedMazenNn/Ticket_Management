from django.contrib import admin

from .models import TicketHistory


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "ticket", "changed_by", "field_name", "created_at"]
    list_filter = ["field_name", "created_at"]
    readonly_fields = [
        "id",
        "ticket",
        "changed_by",
        "field_name",
        "old_value",
        "new_value",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
