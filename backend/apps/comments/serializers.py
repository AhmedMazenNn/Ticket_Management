from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment

User = get_user_model()


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]
        read_only_fields = fields


class CommentCreateSerializer(serializers.Serializer):
    body = serializers.CharField()

    def validate_body(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Body cannot be empty.")
        return value.strip()


class CommentUpdateSerializer(serializers.Serializer):
    body = serializers.CharField()

    def validate_body(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Body cannot be empty.")
        return value.strip()


class CommentDetailSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "ticket",
            "author",
            "body",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "ticket", "author", "created_at", "updated_at"]
