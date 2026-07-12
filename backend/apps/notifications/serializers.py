from rest_framework import serializers

from apps.tickets.serializers import TicketListSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    ticket = TicketListSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "ticket", "type", "status", "is_read", "sent_at", "created_at"]
        read_only_fields = fields
