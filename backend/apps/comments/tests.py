import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.factories import AdminUserFactory, UserFactory
from apps.tickets.factories import TicketFactory

from .factories import CommentFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_user():
    return AdminUserFactory()


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def ticket(user):
    return TicketFactory(created_by=user)


class TestCreateComment:
    def test_create_comment(self, auth_client, ticket):
        data = {"body": "This is a comment."}
        response = auth_client.post(
            f"/api/tickets/{ticket.id}/comments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["body"] == "This is a comment."
        assert "author" in response.data
        assert "id" in response.data["author"]

    def test_create_comment_empty_body(self, auth_client, ticket):
        data = {"body": ""}
        response = auth_client.post(
            f"/api/tickets/{ticket.id}/comments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_whitespace_only_body(self, auth_client, ticket):
        data = {"body": "   "}
        response = auth_client.post(
            f"/api/tickets/{ticket.id}/comments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_missing_body(self, auth_client, ticket):
        response = auth_client.post(
            f"/api/tickets/{ticket.id}/comments/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_ticket_not_found(self, auth_client):
        fake_id = uuid.uuid4()
        data = {"body": "Comment on non-existent ticket."}
        response = auth_client.post(
            f"/api/tickets/{fake_id}/comments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_comment_unauthenticated(self, api_client, ticket):
        data = {"body": "Unauthenticated comment."}
        response = api_client.post(
            f"/api/tickets/{ticket.id}/comments/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListComments:
    def test_list_comments(self, auth_client, ticket):
        CommentFactory(ticket=ticket)
        CommentFactory(ticket=ticket)
        response = auth_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_comments_newest_first(self, auth_client, ticket):
        CommentFactory(ticket=ticket, body="Older")
        CommentFactory(ticket=ticket, body="Newer")
        response = auth_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["body"] == "Newer"
        assert response.data[1]["body"] == "Older"

    def test_list_comments_ticket_not_found(self, auth_client):
        fake_id = uuid.uuid4()
        response = auth_client.get(f"/api/tickets/{fake_id}/comments/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_comments_unauthenticated(self, api_client, ticket):
        response = api_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_comments_empty(self, auth_client, ticket):
        response = auth_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


class TestUpdateComment:
    def test_update_own_comment(self, auth_client, ticket, user):
        comment = CommentFactory(ticket=ticket, author=user, body="Original body.")
        data = {"body": "Updated body."}
        response = auth_client.put(
            f"/api/comments/{comment.id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == "Updated body."

    def test_update_comment_empty_body(self, auth_client, ticket, user):
        comment = CommentFactory(ticket=ticket, author=user, body="Original.")
        data = {"body": ""}
        response = auth_client.put(
            f"/api/comments/{comment.id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_another_users_comment(self, auth_client, ticket):
        other_user = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other_user, body="Not yours.")
        data = {"body": "Trying to edit."}
        response = auth_client.put(
            f"/api/comments/{comment.id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_comment_not_found(self, auth_client):
        fake_id = uuid.uuid4()
        data = {"body": "Updated."}
        response = auth_client.put(
            f"/api/comments/{fake_id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_comment_unauthenticated(self, api_client, ticket):
        comment = CommentFactory(ticket=ticket, body="Original.")
        data = {"body": "Updated."}
        response = api_client.put(
            f"/api/comments/{comment.id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_update_any_comment(self, admin_client, ticket):
        other_user = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other_user, body="Admin edit.")
        data = {"body": "Admin updated."}
        response = admin_client.put(
            f"/api/comments/{comment.id}/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == "Admin updated."


class TestDeleteComment:
    def test_delete_own_comment(self, auth_client, ticket, user):
        comment = CommentFactory(ticket=ticket, author=user, body="To be deleted.")
        response = auth_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_another_users_comment(self, auth_client, ticket):
        other_user = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other_user, body="Not yours.")
        response = auth_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_not_found(self, auth_client):
        fake_id = uuid.uuid4()
        response = auth_client.delete(f"/api/comments/{fake_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment_unauthenticated(self, api_client, ticket):
        comment = CommentFactory(ticket=ticket, body="To be deleted.")
        response = api_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_delete_any_comment(self, admin_client, ticket):
        other_user = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other_user, body="Admin delete.")
        response = admin_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
