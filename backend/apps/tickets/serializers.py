from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Ticket

User = get_user_model()


class TicketUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]
        read_only_fields = fields


class TicketListSerializer(serializers.ModelSerializer):
    assigned_to = TicketUserSerializer(read_only=True)
    created_by = TicketUserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "priority",
            "status",
            "assigned_to",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class TicketDetailSerializer(serializers.ModelSerializer):
    assigned_to = TicketUserSerializer(read_only=True)
    created_by = TicketUserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
        ]
        read_only_fields = ["id"]

    def validate_assigned_to(self, value):
        if value is not None and not value.is_active:
            raise serializers.ValidationError("Cannot assign to an inactive user.")
        return value


class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
        ]

    def validate_assigned_to(self, value):
        if value is not None and not value.is_active:
            raise serializers.ValidationError("Cannot assign to an inactive user.")
        return value
