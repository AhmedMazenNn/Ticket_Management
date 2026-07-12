from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "ticket", "user", "type", "status", "is_read", "created_at", "sent_at"]
    list_filter = ["type", "status", "is_read"]
    readonly_fields = ["id", "ticket", "user", "type", "status", "is_read", "created_at", "sent_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
