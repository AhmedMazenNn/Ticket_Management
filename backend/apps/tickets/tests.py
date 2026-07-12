import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.factories import AdminUserFactory, UserFactory
from apps.accounts.models import User

from .factories import TicketFactory
from .models import Ticket

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
# Ticket Creation
# ---------------------------------------------------------------------------


class TestTicketCreate:
    def test_manager_can_create_ticket(self, manager_client, manager):
        data = {"title": "New Bug Report", "description": "Something is broken", "priority": "HIGH"}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Bug Report"
        assert response.data["created_by"]["id"] == str(manager.id)

    def test_admin_can_create_ticket(self, admin_client):
        data = {"title": "Admin Ticket"}
        response = admin_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_agent_cannot_create_ticket(self, agent_client):
        data = {"title": "Agent Ticket"}
        response = agent_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_ticket_missing_title(self, manager_client):
        data = {"description": "No title"}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_ticket_unauthenticated(self, api_client):
        data = {"title": "Unauthorized"}
        response = api_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_ticket_assign_agent(self, manager_client, agent):
        data = {"title": "Assigned Ticket", "assigned_to": str(agent.id)}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["assigned_to"]["id"] == str(agent.id)

    def test_create_ticket_cannot_assign_manager(self, manager_client):
        other_manager = UserFactory(role=User.Role.MANAGER)
        data = {"title": "Bad Assignment", "assigned_to": str(other_manager.id)}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "assigned_to" in response.data

    def test_create_ticket_cannot_assign_admin(self, manager_client, admin_user):
        data = {"title": "Bad Assignment", "assigned_to": str(admin_user.id)}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_assign_ticket_to_self(self, admin_client, admin_user):
        data = {"title": "Self-assigned", "assigned_to": str(admin_user.id)}
        response = admin_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["assigned_to"]["id"] == str(admin_user.id)

    def test_manager_can_assign_ticket_to_self(self, manager_client, manager):
        data = {"title": "Self-assigned", "assigned_to": str(manager.id)}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["assigned_to"]["id"] == str(manager.id)

    def test_admin_cannot_assign_to_other_admin(self, admin_client):
        other_admin = AdminUserFactory()
        data = {"title": "Bad", "assigned_to": str(other_admin.id)}
        response = admin_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_manager_cannot_assign_to_other_manager(self, manager_client):
        other_manager = UserFactory(role=User.Role.MANAGER)
        data = {"title": "Bad", "assigned_to": str(other_manager.id)}
        response = manager_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Ticket Retrieve
# ---------------------------------------------------------------------------


class TestTicketRetrieve:
    def test_manager_can_retrieve_any_ticket(self, manager_client):
        ticket = TicketFactory()
        response = manager_client.get(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(ticket.id)

    def test_agent_can_retrieve_assigned_ticket(self, agent_client, agent):
        ticket = TicketFactory(assigned_to=agent)
        response = agent_client.get(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_agent_cannot_retrieve_unassigned_ticket(self, agent_client):
        ticket = TicketFactory()
        response = agent_client.get(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_ticket_not_found(self, manager_client):
        import uuid

        fake_id = uuid.uuid4()
        response = manager_client.get(f"/api/tickets/{fake_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Ticket Update
# ---------------------------------------------------------------------------


class TestTicketUpdate:
    def test_manager_can_update_all_fields(self, manager_client, agent):
        ticket = TicketFactory()
        data = {"title": "Updated", "priority": "LOW", "status": "IN_PROGRESS", "assigned_to": str(agent.id)}
        response = manager_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated"
        assert response.data["priority"] == "LOW"

    def test_agent_can_update_status_on_assigned_ticket(self, agent_client, agent):
        ticket = TicketFactory(assigned_to=agent)
        data = {"status": "IN_PROGRESS"}
        response = agent_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "IN_PROGRESS"

    def test_agent_cannot_update_title_on_assigned_ticket(self, agent_client, agent):
        ticket = TicketFactory(assigned_to=agent)
        data = {"title": "Hacked Title"}
        response = agent_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_agent_cannot_update_unassigned_ticket(self, agent_client):
        ticket = TicketFactory()
        data = {"status": "CLOSED"}
        response = agent_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_ticket_unauthenticated(self, api_client):
        ticket = TicketFactory()
        response = api_client.patch(f"/api/tickets/{ticket.id}/", {"title": "X"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket Delete
# ---------------------------------------------------------------------------


class TestTicketDelete:
    def test_manager_can_delete_ticket(self, manager_client):
        ticket = TicketFactory()
        response = manager_client.delete(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_agent_cannot_delete_ticket(self, agent_client, agent):
        ticket = TicketFactory(assigned_to=agent)
        response = agent_client.delete(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Ticket List
# ---------------------------------------------------------------------------


class TestTicketList:
    def test_manager_sees_all_tickets(self, manager_client):
        TicketFactory.create_batch(3)
        response = manager_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_agent_sees_only_assigned_tickets(self, agent_client, agent):
        TicketFactory(assigned_to=agent)
        TicketFactory(assigned_to=agent)
        TicketFactory()  # not assigned to agent
        response = agent_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_list_tickets_unauthenticated(self, api_client):
        response = api_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket Filtering
# ---------------------------------------------------------------------------


class TestTicketFilter:
    def test_filter_by_status(self, manager_client):
        TicketFactory(status=Ticket.Status.OPEN)
        TicketFactory(status=Ticket.Status.CLOSED)
        response = manager_client.get("/api/tickets/?status=OPEN")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_priority(self, manager_client):
        TicketFactory(priority=Ticket.Priority.LOW)
        TicketFactory(priority=Ticket.Priority.HIGH)
        response = manager_client.get("/api/tickets/?priority=HIGH")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


# ---------------------------------------------------------------------------
# Ticket Search
# ---------------------------------------------------------------------------


class TestTicketSearch:
    def test_search_by_title(self, manager_client):
        TicketFactory(title="Login page broken")
        TicketFactory(title="Database migration issue")
        response = manager_client.get("/api/tickets/?search=Login")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


# ---------------------------------------------------------------------------
# Ticket Permissions
# ---------------------------------------------------------------------------


class TestTicketPermissions:
    def test_unauthenticated_create(self, api_client):
        response = api_client.post("/api/tickets/", {"title": "Test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_list(self, api_client):
        response = api_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_update(self, api_client):
        ticket = TicketFactory()
        response = api_client.patch(f"/api/tickets/{ticket.id}/", {"title": "X"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_delete(self, api_client):
        ticket = TicketFactory()
        response = api_client.delete(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
