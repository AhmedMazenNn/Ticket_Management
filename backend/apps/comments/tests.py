import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.factories import AdminUserFactory, UserFactory
from apps.accounts.models import User
from apps.tickets.factories import TicketFactory

from .factories import CommentFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def agent():
    return UserFactory(role=User.Role.AGENT)


@pytest.fixture
def agent_client(agent):
    client = APIClient()
    client.force_authenticate(user=agent)
    return client


@pytest.fixture
def manager():
    return UserFactory(role=User.Role.MANAGER)


@pytest.fixture
def manager_client(manager):
    client = APIClient()
    client.force_authenticate(user=manager)
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
def ticket(manager):
    return TicketFactory(created_by=manager)


@pytest.fixture
def agent_ticket(manager, agent):
    return TicketFactory(created_by=manager, assigned_to=agent)


# ---------------------------------------------------------------------------
# Create Comment
# ---------------------------------------------------------------------------


class TestCreateComment:
    def test_manager_can_comment_on_any_ticket(self, manager_client, ticket):
        data = {"body": "Manager comment."}
        response = manager_client.post(
            f"/api/tickets/{ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["body"] == "Manager comment."

    def test_admin_can_comment_on_any_ticket(self, admin_client, ticket):
        data = {"body": "Admin comment."}
        response = admin_client.post(
            f"/api/tickets/{ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_agent_can_comment_on_assigned_ticket(self, agent_client, agent_ticket):
        data = {"body": "Agent comment."}
        response = agent_client.post(
            f"/api/tickets/{agent_ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_agent_cannot_comment_on_unassigned_ticket(self, agent_client, ticket):
        data = {"body": "Unauthorized comment."}
        response = agent_client.post(
            f"/api/tickets/{ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_comment_empty_body(self, manager_client, ticket):
        data = {"body": ""}
        response = manager_client.post(
            f"/api/tickets/{ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_whitespace_only_body(self, manager_client, ticket):
        data = {"body": "   "}
        response = manager_client.post(
            f"/api/tickets/{ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_missing_body(self, manager_client, ticket):
        response = manager_client.post(
            f"/api/tickets/{ticket.id}/comments/", {}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_ticket_not_found(self, manager_client):
        fake_id = uuid.uuid4()
        data = {"body": "Not found."}
        response = manager_client.post(
            f"/api/tickets/{fake_id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_comment_unauthenticated(self, api_client, ticket):
        data = {"body": "Unauthenticated."}
        response = api_client.post(
            f"/api/tickets/{ticket.id}/comments/", data, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# List Comments
# ---------------------------------------------------------------------------


class TestListComments:
    def test_list_comments(self, manager_client, ticket):
        CommentFactory(ticket=ticket)
        CommentFactory(ticket=ticket)
        response = manager_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_comments_newest_first(self, manager_client, ticket):
        CommentFactory(ticket=ticket, body="Older")
        CommentFactory(ticket=ticket, body="Newer")
        response = manager_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["body"] == "Newer"
        assert response.data[1]["body"] == "Older"

    def test_list_comments_ticket_not_found(self, manager_client):
        fake_id = uuid.uuid4()
        response = manager_client.get(f"/api/tickets/{fake_id}/comments/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_comments_unauthenticated(self, api_client, ticket):
        response = api_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_comments_empty(self, manager_client, ticket):
        response = manager_client.get(f"/api/tickets/{ticket.id}/comments/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


# ---------------------------------------------------------------------------
# Update Comment
# ---------------------------------------------------------------------------


class TestUpdateComment:
    def test_update_own_comment(self, manager_client, ticket, manager):
        comment = CommentFactory(ticket=ticket, author=manager, body="Original.")
        data = {"body": "Updated."}
        response = manager_client.put(
            f"/api/comments/{comment.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == "Updated."

    def test_update_comment_empty_body(self, manager_client, ticket, manager):
        comment = CommentFactory(ticket=ticket, author=manager, body="Original.")
        data = {"body": ""}
        response = manager_client.put(
            f"/api/comments/{comment.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_another_users_comment(self, manager_client, ticket):
        other = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other, body="Not yours.")
        data = {"body": "Trying to edit."}
        response = manager_client.put(
            f"/api/comments/{comment.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_comment_not_found(self, manager_client):
        fake_id = uuid.uuid4()
        data = {"body": "Updated."}
        response = manager_client.put(
            f"/api/comments/{fake_id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_comment_unauthenticated(self, api_client, ticket):
        comment = CommentFactory(ticket=ticket, body="Original.")
        data = {"body": "Updated."}
        response = api_client.put(
            f"/api/comments/{comment.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_update_any_comment(self, admin_client, ticket):
        other = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other, body="Admin edit.")
        data = {"body": "Admin updated."}
        response = admin_client.put(
            f"/api/comments/{comment.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["body"] == "Admin updated."


# ---------------------------------------------------------------------------
# Delete Comment
# ---------------------------------------------------------------------------


class TestDeleteComment:
    def test_delete_own_comment(self, manager_client, ticket, manager):
        comment = CommentFactory(ticket=ticket, author=manager, body="Delete me.")
        response = manager_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_another_users_comment(self, manager_client, ticket):
        other = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other, body="Not yours.")
        response = manager_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_comment_not_found(self, manager_client):
        fake_id = uuid.uuid4()
        response = manager_client.delete(f"/api/comments/{fake_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment_unauthenticated(self, api_client, ticket):
        comment = CommentFactory(ticket=ticket, body="Delete me.")
        response = api_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_delete_any_comment(self, admin_client, ticket):
        other = UserFactory()
        comment = CommentFactory(ticket=ticket, author=other, body="Admin delete.")
        response = admin_client.delete(f"/api/comments/{comment.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
