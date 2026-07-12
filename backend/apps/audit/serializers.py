from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import TicketHistory

User = get_user_model()


class HistoryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]
        read_only_fields = fields


class TicketHistorySerializer(serializers.ModelSerializer):
    changed_by = HistoryUserSerializer(read_only=True)

    class Meta:
        model = TicketHistory
        fields = [
            "id",
            "field_name",
            "old_value",
            "new_value",
            "changed_by",
            "created_at",
        ]
        read_only_fields = fields
