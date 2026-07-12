import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.factories import AdminUserFactory, UserFactory
from apps.accounts.models import User
from apps.tickets.factories import TicketFactory

from .factories import NotificationFactory
from .models import Notification

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
# Notification Model
# ---------------------------------------------------------------------------


class TestNotificationModel:
    def test_new_notification_is_unread_by_default(self, manager):
        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(ticket=ticket, user=manager)
        assert notif.is_read is False

    def test_notification_str(self, manager):
        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED
        )
        assert "TICKET_ASSIGNED" in str(notif)
        assert manager.email in str(notif)


# ---------------------------------------------------------------------------
# List Notifications
# ---------------------------------------------------------------------------


class TestListNotifications:
    def test_user_sees_own_notifications(self, manager_client, manager):
        ticket = TicketFactory(created_by=manager)
        NotificationFactory(ticket=ticket, user=manager)
        NotificationFactory(ticket=ticket, user=manager)
        response = manager_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_user_does_not_see_other_users_notifications(self, manager_client, manager):
        other = UserFactory()
        ticket = TicketFactory(created_by=manager)
        NotificationFactory(ticket=ticket, user=other)
        response = manager_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0

    def test_notifications_ordered_newest_first(self, manager_client, manager):
        ticket = TicketFactory(created_by=manager)
        older = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED
        )
        newer = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.STATUS_CHANGED
        )
        response = manager_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["id"] == str(newer.id)
        assert results[1]["id"] == str(older.id)

    def test_unauthenticated_list_returns_401(self, api_client):
        response = api_client.get("/api/notifications/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Retrieve Notification
# ---------------------------------------------------------------------------


class TestRetrieveNotification:
    def test_owner_can_retrieve_notification(self, manager_client, manager):
        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(ticket=ticket, user=manager)
        response = manager_client.get(f"/api/notifications/{notif.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(notif.id)

    def test_non_owner_gets_404(self, manager_client):
        other = UserFactory()
        ticket = TicketFactory()
        notif = NotificationFactory(ticket=ticket, user=other)
        response = manager_client.get(f"/api/notifications/{notif.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nonexistent_notification_returns_404(self, manager_client):
        import uuid

        fake_id = uuid.uuid4()
        response = manager_client.get(f"/api/notifications/{fake_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_detail_returns_401(self, api_client):
        notif = NotificationFactory()
        response = api_client.get(f"/api/notifications/{notif.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Mark as Read
# ---------------------------------------------------------------------------


class TestMarkRead:
    def test_owner_can_mark_as_read(self, manager_client, manager):
        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(ticket=ticket, user=manager, is_read=False)
        response = manager_client.patch(f"/api/notifications/{notif.id}/read/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_read"] is True

    def test_non_owner_cannot_mark_as_read(self, manager_client):
        other = UserFactory()
        ticket = TicketFactory()
        notif = NotificationFactory(ticket=ticket, user=other)
        response = manager_client.patch(f"/api/notifications/{notif.id}/read/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_mark_read_returns_401(self, api_client):
        notif = NotificationFactory()
        response = api_client.patch(f"/api/notifications/{notif.id}/read/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Ticket Assignment Integration
# ---------------------------------------------------------------------------


class TestAssignmentNotification:
    def test_create_ticket_with_assignee_creates_notification(self, manager, agent):
        from apps.tickets.services import create_ticket

        ticket = create_ticket(
            title="Test",
            assigned_to=agent,
            created_by=manager,
        )
        notifications = Notification.objects.filter(
            ticket=ticket, user=agent, type=Notification.Type.TICKET_ASSIGNED
        )
        assert notifications.count() == 1

    def test_create_ticket_without_assignee_creates_no_notification(self, manager):
        from apps.tickets.services import create_ticket

        ticket = create_ticket(
            title="Test",
            assigned_to=None,
            created_by=manager,
        )
        notifications = Notification.objects.filter(ticket=ticket)
        assert notifications.count() == 0

    def test_create_ticket_self_assign_creates_no_notification(self, manager):
        from apps.tickets.services import create_ticket

        ticket = create_ticket(
            title="Test",
            assigned_to=manager,
            created_by=manager,
        )
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.TICKET_ASSIGNED
        )
        assert notifications.count() == 0

    def test_assign_ticket_creates_notification(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=None)
        from apps.tickets.services import assign_ticket

        assign_ticket(ticket, agent, changed_by=manager)
        notifications = Notification.objects.filter(
            ticket=ticket, user=agent, type=Notification.Type.TICKET_ASSIGNED
        )
        assert notifications.count() == 1

    def test_assign_ticket_self_assign_creates_no_notification(self, manager):
        ticket = TicketFactory(created_by=manager, assigned_to=None)
        from apps.tickets.services import assign_ticket

        assign_ticket(ticket, manager, changed_by=manager)
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.TICKET_ASSIGNED
        )
        assert notifications.count() == 0


# ---------------------------------------------------------------------------
# Ticket Update Integration
# ---------------------------------------------------------------------------


class TestTicketUpdateNotification:
    def test_status_change_creates_notification(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.tickets.services import update_ticket

        update_ticket(ticket, changed_by=manager, status="IN_PROGRESS")
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.STATUS_CHANGED
        )
        assert notifications.count() == 1  # agent only (manager is changed_by)

    def test_priority_change_creates_notification(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.tickets.services import update_ticket

        update_ticket(ticket, changed_by=manager, priority="HIGH")
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.PRIORITY_CHANGED
        )
        assert notifications.count() == 1  # agent only (manager is changed_by)

    def test_title_change_creates_notification(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.tickets.services import update_ticket

        update_ticket(ticket, changed_by=agent, title="New Title")
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.TICKET_UPDATED
        )
        assert notifications.count() == 1  # only manager (agent is changed_by)

    def test_no_notification_on_unchanged_value(self, manager):
        ticket = TicketFactory(created_by=manager, status="OPEN")
        from apps.tickets.services import update_ticket

        update_ticket(ticket, changed_by=manager, status="OPEN")
        notifications = Notification.objects.filter(ticket=ticket)
        assert notifications.count() == 0

    def test_update_by_creator_no_self_notification(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.tickets.services import update_ticket

        update_ticket(ticket, changed_by=manager, title="Updated")
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.TICKET_UPDATED
        )
        assert notifications.count() == 1  # only agent


# ---------------------------------------------------------------------------
# Comment Integration
# ---------------------------------------------------------------------------


class TestCommentNotification:
    def test_comment_creates_notification_for_creator(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.comments.services import create_comment

        create_comment(ticket=ticket, author=agent, body="Hello")
        notifications = Notification.objects.filter(
            ticket=ticket, user=manager, type=Notification.Type.COMMENT_ADDED
        )
        assert notifications.count() == 1

    def test_comment_creates_notification_for_assignee(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.comments.services import create_comment

        create_comment(ticket=ticket, author=manager, body="Hello")
        notifications = Notification.objects.filter(
            ticket=ticket, user=agent, type=Notification.Type.COMMENT_ADDED
        )
        assert notifications.count() == 1

    def test_comment_no_self_notification_for_creator(self, manager):
        ticket = TicketFactory(created_by=manager, assigned_to=None)
        from apps.comments.services import create_comment

        create_comment(ticket=ticket, author=manager, body="Self comment")
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.COMMENT_ADDED
        )
        assert notifications.count() == 0

    def test_comment_no_self_notification_for_assignee(self, manager, agent):
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.comments.services import create_comment

        create_comment(ticket=ticket, author=agent, body="Self comment")
        notifications = Notification.objects.filter(
            ticket=ticket, user=agent, type=Notification.Type.COMMENT_ADDED
        )
        assert notifications.count() == 0

    def test_comment_notifies_both_when_different_users(self, manager, agent):
        other = UserFactory()
        ticket = TicketFactory(created_by=manager, assigned_to=agent)
        from apps.comments.services import create_comment

        create_comment(ticket=ticket, author=other, body="Third party comment")
        notifications = Notification.objects.filter(
            ticket=ticket, type=Notification.Type.COMMENT_ADDED
        )
        assert notifications.count() == 2  # manager + agent
