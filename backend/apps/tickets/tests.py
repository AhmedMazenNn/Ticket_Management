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
        data = {
            "title": "Updated",
            "priority": "LOW",
            "status": "IN_PROGRESS",
            "assigned_to": str(agent.id),
        }
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


# ---------------------------------------------------------------------------
# Dashboard Cache
# ---------------------------------------------------------------------------


class TestDashboardCache:
    def test_dashboard_stats_cached_on_first_request(self, manager_client):
        from django.core.cache import cache

        cache.clear()
        TicketFactory.create_batch(3)

        response1 = manager_client.get("/api/tickets/dashboard_stats/")
        assert response1.status_code == status.HTTP_200_OK
        assert response1.data["total"] == 3

        cached = cache.get("dashboard_stats")
        assert cached is not None
        assert cached["total"] == 3

    def test_dashboard_stats_returns_cached_data(self, manager_client):
        from django.core.cache import cache

        cache.clear()
        TicketFactory.create_batch(2)

        response1 = manager_client.get("/api/tickets/dashboard_stats/")
        assert response1.data["total"] == 2

        TicketFactory.create_batch(3)

        response2 = manager_client.get("/api/tickets/dashboard_stats/")
        assert response2.data["total"] == 2

    def test_my_stats_cached_per_user(self, manager_client, manager, agent_client, agent):
        from django.core.cache import cache

        cache.clear()
        TicketFactory(assigned_to=agent)
        TicketFactory(assigned_to=agent)
        TicketFactory(created_by=manager)

        manager_client.get("/api/tickets/my_stats/")
        agent_client.get("/api/tickets/my_stats/")

        assert cache.get(f"my_stats_{manager.id}") is not None
        assert cache.get(f"my_stats_{agent.id}") is not None
        assert cache.get(f"my_stats_{manager.id}") != cache.get(f"my_stats_{agent.id}")

    def test_cache_uses_300s_timeout(self, manager_client):
        from django.core.cache import cache

        cache.clear()
        TicketFactory()

        manager_client.get("/api/tickets/dashboard_stats/")

        cached = cache.get("dashboard_stats")
        assert cached is not None

    def test_cache_invalidated_on_ticket_create(self, manager_client, manager):
        from django.core.cache import cache

        cache.clear()
        manager_client.get("/api/tickets/dashboard_stats/")
        manager_client.get("/api/tickets/my_stats/")
        assert cache.get("dashboard_stats") is not None
        assert cache.get(f"my_stats_{manager.id}") is not None

        manager_client.post(
            "/api/tickets/",
            {"title": "New Ticket"},
            format="json",
        )
        assert cache.get("dashboard_stats") is None
        assert cache.get(f"my_stats_{manager.id}") is None

    def test_cache_invalidated_on_ticket_update(self, manager_client, manager):
        from django.core.cache import cache

        cache.clear()
        ticket = TicketFactory(created_by=manager)
        manager_client.get("/api/tickets/dashboard_stats/")
        assert cache.get("dashboard_stats") is not None

        manager_client.patch(
            f"/api/tickets/{ticket.id}/",
            {"title": "Updated Title"},
            format="json",
        )
        assert cache.get("dashboard_stats") is None

    def test_cache_invalidated_on_ticket_delete(self, manager_client):
        from django.core.cache import cache

        cache.clear()
        ticket = TicketFactory()
        manager_client.get("/api/tickets/dashboard_stats/")
        assert cache.get("dashboard_stats") is not None

        manager_client.delete(f"/api/tickets/{ticket.id}/")
        assert cache.get("dashboard_stats") is None

    def test_cache_invalidated_on_status_change(self, manager_client):
        from django.core.cache import cache

        cache.clear()
        ticket = TicketFactory()
        manager_client.get("/api/tickets/dashboard_stats/")
        assert cache.get("dashboard_stats") is not None

        manager_client.patch(
            f"/api/tickets/{ticket.id}/",
            {"status": "IN_PROGRESS"},
            format="json",
        )
        assert cache.get("dashboard_stats") is None

    def test_cache_invalidated_on_assignment(self, manager_client, agent):
        from django.core.cache import cache

        cache.clear()
        ticket = TicketFactory()
        manager_client.get("/api/tickets/dashboard_stats/")
        manager_client.get("/api/tickets/my_stats/")
        assert cache.get("dashboard_stats") is not None

        manager_client.patch(
            f"/api/tickets/{ticket.id}/",
            {"assigned_to": str(agent.id)},
            format="json",
        )
        assert cache.get("dashboard_stats") is None
        assert cache.get(f"my_stats_{agent.id}") is None


# ---------------------------------------------------------------------------
# Transaction Safety — on_commit
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestTicketTransactionSafety:
    def test_event_dispatched_on_successful_commit(self, manager):
        """When the transaction commits, publish_event is called."""
        from unittest.mock import patch

        from django.db import transaction

        from apps.tickets.services import create_ticket

        with patch("apps.tickets.services.publish_event") as mock_publish:
            with transaction.atomic():
                create_ticket(title="Tx test", created_by=manager)
            mock_publish.assert_called_once()

    def test_no_event_dispatched_on_ticket_create_rollback(self, manager):
        """When the transaction rolls back on create_ticket, no event is published."""
        from unittest.mock import patch

        from django.db import transaction
        from django.db.utils import IntegrityError

        from apps.tickets.services import create_ticket

        with patch("apps.tickets.services.publish_event") as mock_publish:
            try:
                with transaction.atomic():
                    create_ticket(title="Rollback test", created_by=manager)
                    raise IntegrityError("simulated rollback")
            except IntegrityError:
                pass

            mock_publish.assert_not_called()

    def test_no_event_dispatched_on_ticket_update_rollback(self, manager):
        """When the transaction rolls back on update_ticket, no event is published."""
        from unittest.mock import patch

        from django.db import transaction
        from django.db.utils import IntegrityError

        from apps.tickets.services import update_ticket

        ticket = TicketFactory(created_by=manager)

        with patch("apps.tickets.services.publish_event") as mock_publish:
            try:
                with transaction.atomic():
                    update_ticket(ticket, changed_by=manager, title="Updated")
                    raise IntegrityError("simulated rollback")
            except IntegrityError:
                pass

            mock_publish.assert_not_called()

    def test_no_event_dispatched_on_assign_ticket_rollback(self, manager, agent):
        """When the transaction rolls back on assign_ticket, no event is published."""
        from unittest.mock import patch

        from django.db import transaction
        from django.db.utils import IntegrityError

        from apps.tickets.services import assign_ticket

        ticket = TicketFactory(created_by=manager)

        with patch("apps.tickets.services.publish_event") as mock_publish:
            try:
                with transaction.atomic():
                    assign_ticket(ticket, agent, changed_by=manager)
                    raise IntegrityError("simulated rollback")
            except IntegrityError:
                pass

            mock_publish.assert_not_called()

    def test_no_ticket_persisted_on_rollback(self, manager):
        """When the transaction rolls back, the ticket row is gone."""
        from unittest.mock import patch

        from django.db import transaction
        from django.db.utils import IntegrityError

        from apps.tickets.services import create_ticket

        initial_count = Ticket.objects.count()

        with patch("apps.tickets.services.publish_event"):
            try:
                with transaction.atomic():
                    create_ticket(title="Rollback test", created_by=manager)
                    raise IntegrityError("simulated rollback")
            except IntegrityError:
                pass

        assert Ticket.objects.count() == initial_count
