import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.factories import UserFactory

from .factories import TicketFactory
from .models import Ticket

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
def other_user():
    return UserFactory()


# ---------------------------------------------------------------------------
# Ticket Creation
# ---------------------------------------------------------------------------


class TestTicketCreate:
    def test_create_ticket_success(self, auth_client, user):
        data = {
            "title": "New Bug Report",
            "description": "Something is broken",
            "priority": "HIGH",
            "status": "OPEN",
        }
        response = auth_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Bug Report"
        assert response.data["priority"] == "HIGH"
        assert response.data["created_by"]["id"] == str(user.id)

    def test_create_ticket_minimal_fields(self, auth_client):
        data = {"title": "Minimal Ticket"}
        response = auth_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priority"] == "MEDIUM"
        assert response.data["status"] == "OPEN"

    def test_create_ticket_missing_title(self, auth_client):
        data = {"description": "No title provided"}
        response = auth_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

    def test_create_ticket_invalid_priority(self, auth_client):
        data = {"title": "Test", "priority": "CRITICAL"}
        response = auth_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "priority" in response.data

    def test_create_ticket_invalid_status(self, auth_client):
        data = {"title": "Test", "status": "PENDING"}
        response = auth_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "status" in response.data

    def test_create_ticket_unauthenticated(self, api_client):
        data = {"title": "Unauthorized"}
        response = api_client.post("/api/tickets/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket Retrieve
# ---------------------------------------------------------------------------


class TestTicketRetrieve:
    def test_retrieve_ticket_success(self, auth_client):
        ticket = TicketFactory()
        response = auth_client.get(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(ticket.id)
        assert response.data["title"] == ticket.title
        assert "description" in response.data

    def test_retrieve_ticket_not_found(self, auth_client):
        import uuid

        fake_id = uuid.uuid4()
        response = auth_client.get(f"/api/tickets/{fake_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_ticket_unauthenticated(self, api_client):
        ticket = TicketFactory()
        response = api_client.get(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket Update
# ---------------------------------------------------------------------------


class TestTicketUpdate:
    def test_patch_ticket_success(self, auth_client):
        ticket = TicketFactory()
        data = {"title": "Updated Title", "priority": "LOW"}
        response = auth_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"
        assert response.data["priority"] == "LOW"

    def test_put_ticket_success(self, auth_client):
        ticket = TicketFactory()
        data = {
            "title": "Full Update",
            "description": "Updated description",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
        }
        response = auth_client.put(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Full Update"
        assert response.data["status"] == "IN_PROGRESS"

    def test_update_ticket_unauthenticated(self, api_client):
        ticket = TicketFactory()
        data = {"title": "Hacked"}
        response = api_client.patch(f"/api/tickets/{ticket.id}/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket Delete
# ---------------------------------------------------------------------------


class TestTicketDelete:
    def test_delete_ticket_success(self, auth_client):
        ticket = TicketFactory()
        response = auth_client.delete(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Ticket.objects.filter(id=ticket.id).exists()

    def test_delete_ticket_unauthenticated(self, api_client):
        ticket = TicketFactory()
        response = api_client.delete(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket List
# ---------------------------------------------------------------------------


class TestTicketList:
    def test_list_tickets_success(self, auth_client):
        TicketFactory.create_batch(3)
        response = auth_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

    def test_list_tickets_unauthenticated(self, api_client):
        response = api_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tickets_pagination(self, auth_client):
        TicketFactory.create_batch(25)
        response = auth_client.get("/api/tickets/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 25
        assert len(response.data["results"]) == 20

        response_page2 = auth_client.get("/api/tickets/?page=2")
        assert response_page2.status_code == status.HTTP_200_OK
        assert len(response_page2.data["results"]) == 5


# ---------------------------------------------------------------------------
# Ticket Filtering
# ---------------------------------------------------------------------------


class TestTicketFilter:
    def test_filter_by_status(self, auth_client):
        TicketFactory(status=Ticket.Status.OPEN)
        TicketFactory(status=Ticket.Status.CLOSED)
        response = auth_client.get("/api/tickets/?status=OPEN")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["status"] == "OPEN"

    def test_filter_by_priority(self, auth_client):
        TicketFactory(priority=Ticket.Priority.LOW)
        TicketFactory(priority=Ticket.Priority.HIGH)
        response = auth_client.get("/api/tickets/?priority=HIGH")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["priority"] == "HIGH"

    def test_filter_by_created_by(self, auth_client, user):
        TicketFactory(created_by=user)
        other = UserFactory()
        TicketFactory(created_by=other)
        response = auth_client.get(f"/api/tickets/?created_by={user.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_assigned_to(self, auth_client, user):
        TicketFactory(assigned_to=user)
        other = UserFactory()
        TicketFactory(assigned_to=other)
        response = auth_client.get(f"/api/tickets/?assigned_to={user.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


# ---------------------------------------------------------------------------
# Ticket Search
# ---------------------------------------------------------------------------


class TestTicketSearch:
    def test_search_by_title(self, auth_client):
        TicketFactory(title="Login page broken")
        TicketFactory(title="Database migration issue")
        response = auth_client.get("/api/tickets/?search=Login")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert "Login" in response.data["results"][0]["title"]

    def test_search_by_description(self, auth_client):
        TicketFactory(title="Ticket A", description="Payment gateway failing")
        TicketFactory(title="Ticket B", description="Unrelated content")
        response = auth_client.get("/api/tickets/?search=Payment")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_search_no_results(self, auth_client):
        TicketFactory(title="Something")
        response = auth_client.get("/api/tickets/?search=nonexistent")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


# ---------------------------------------------------------------------------
# Ticket Ordering
# ---------------------------------------------------------------------------


class TestTicketOrdering:
    def test_ordering_by_created_at(self, auth_client):
        t1 = TicketFactory()
        t2 = TicketFactory()
        response = auth_client.get("/api/tickets/?ordering=created_at")
        assert response.status_code == status.HTTP_200_OK
        ids = [t["id"] for t in response.data["results"]]
        assert ids[0] == str(t1.id)
        assert ids[1] == str(t2.id)

    def test_ordering_by_priority(self, auth_client):
        TicketFactory(priority=Ticket.Priority.HIGH)
        TicketFactory(priority=Ticket.Priority.LOW)
        response = auth_client.get("/api/tickets/?ordering=priority")
        assert response.status_code == status.HTTP_200_OK
        priorities = [t["priority"] for t in response.data["results"]]
        assert priorities == ["HIGH", "LOW"]


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

    def test_unauthenticated_retrieve(self, api_client):
        ticket = TicketFactory()
        response = api_client.get(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_update(self, api_client):
        ticket = TicketFactory()
        response = api_client.patch(f"/api/tickets/{ticket.id}/", {"title": "X"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_delete(self, api_client):
        ticket = TicketFactory()
        response = api_client.delete(f"/api/tickets/{ticket.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
