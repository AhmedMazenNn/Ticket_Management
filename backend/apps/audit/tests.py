import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.factories import AdminUserFactory, UserFactory
from apps.accounts.models import User
from apps.tickets.factories import TicketFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def manager():
    return UserFactory(role=User.Role.MANAGER)


@pytest.fixture
def manager_client(manager):
    client = APIClient()
    client.force_authenticate(user=manager)
    return client


@pytest.fixture
def agent():
    return UserFactory(role=User.Role.AGENT)


@pytest.fixture
def agent_client(agent):
    client = APIClient()
    client.force_authenticate(user=agent)
    return client


@pytest.fixture
def admin_user():
    return AdminUserFactory()


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# ---------------------------------------------------------------------------
# Ticket Creation History
# ---------------------------------------------------------------------------


class TestTicketCreationHistory:
    def test_creation_generates_initial_history_entry(self, manager_client, manager):
        data = {"title": "New Ticket", "description": "A description"}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        ticket_id = response.data["id"]
        history_response = manager_client.get(f"/api/tickets/{ticket_id}/history/")
        assert history_response.status_code == status.HTTP_200_OK
        assert len(history_response.data) == 1

        entry = history_response.data[0]
        assert entry["field_name"] == "created"
        assert entry["old_value"] is None
        assert entry["new_value"] == "Ticket created"
        assert entry["changed_by"]["id"] == str(manager.id)


# ---------------------------------------------------------------------------
# Field Change History
# ---------------------------------------------------------------------------


class TestFieldChangeHistory:
    def test_status_change_creates_history(self, manager_client, agent):
        ticket = TicketFactory()
        data = {"status": "IN_PROGRESS"}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 1
        entry = history_response.data[0]
        assert entry["field_name"] == "status"
        assert entry["old_value"] == "Open"
        assert entry["new_value"] == "In Progress"

    def test_priority_change_creates_history(self, manager_client):
        ticket = TicketFactory(priority="MEDIUM")
        data = {"priority": "HIGH"}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 1
        entry = history_response.data[0]
        assert entry["field_name"] == "priority"
        assert entry["old_value"] == "Medium"
        assert entry["new_value"] == "High"

    def test_assignee_change_creates_history(self, manager_client, agent):
        ticket = TicketFactory(assigned_to=None)
        data = {"assigned_to": str(agent.id)}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 1
        entry = history_response.data[0]
        assert entry["field_name"] == "assigned_to"
        assert entry["old_value"] is None
        assert entry["new_value"] == agent.email

    def test_title_change_creates_history(self, manager_client):
        ticket = TicketFactory(title="Old Title")
        data = {"title": "New Title"}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 1
        entry = history_response.data[0]
        assert entry["field_name"] == "title"
        assert entry["old_value"] == "Old Title"
        assert entry["new_value"] == "New Title"

    def test_description_change_creates_history(self, manager_client):
        ticket = TicketFactory(description="Old description")
        data = {"description": "New description"}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 1
        entry = history_response.data[0]
        assert entry["field_name"] == "description"
        assert entry["old_value"] == "Old description"
        assert entry["new_value"] == "New description"


# ---------------------------------------------------------------------------
# No Change = No History
# ---------------------------------------------------------------------------


class TestNoChangeNoHistory:
    def test_no_history_when_value_unchanged(self, manager_client):
        ticket = TicketFactory(status="OPEN")
        data = {"status": "OPEN"}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 0


# ---------------------------------------------------------------------------
# History Ordering
# ---------------------------------------------------------------------------


class TestHistoryOrdering:
    def test_history_returned_newest_first(self, manager_client):
        ticket = TicketFactory(title="Original", priority="LOW")

        manager_client.patch(
            f"/api/tickets/{ticket.id}/", {"title": "Second"}, format="json"
        )
        manager_client.patch(
            f"/api/tickets/{ticket.id}/", {"priority": "HIGH"}, format="json"
        )

        history_response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert len(history_response.data) == 2

        assert history_response.data[0]["field_name"] == "priority"
        assert history_response.data[1]["field_name"] == "title"


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class TestHistoryPermissions:
    def test_agent_cannot_access_unassigned_ticket_history(self, agent_client, agent):
        ticket = TicketFactory()
        response = agent_client.get(f"/api/tickets/{ticket.id}/history/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_can_access_assigned_ticket_history(self, agent_client, agent):
        ticket = TicketFactory(assigned_to=agent)
        response = agent_client.get(f"/api/tickets/{ticket.id}/history/")
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_access_any_ticket_history(self, manager_client):
        ticket = TicketFactory()
        response = manager_client.get(f"/api/tickets/{ticket.id}/history/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_access_any_ticket_history(self, admin_client):
        ticket = TicketFactory()
        response = admin_client.get(f"/api/tickets/{ticket.id}/history/")
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_access_history(self, api_client):
        ticket = TicketFactory()
        response = api_client.get(f"/api/tickets/{ticket.id}/history/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_history_not_found_for_nonexistent_ticket(self, manager_client):
        import uuid

        fake_id = uuid.uuid4()
        response = manager_client.get(f"/api/tickets/{fake_id}/history/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
