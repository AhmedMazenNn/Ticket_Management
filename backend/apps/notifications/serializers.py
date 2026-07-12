from rest_framework import serializers

from apps.tickets.serializers import TicketListSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    ticket = TicketListSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "ticket", "type", "is_read", "created_at"]
        read_only_fields = fields
