import celery.exceptions
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


# ---------------------------------------------------------------------------
# Notification Model — Status & Sent At
# ---------------------------------------------------------------------------


class TestNotificationStatus:
    def test_new_notification_is_pending_by_default(self, manager):
        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(ticket=ticket, user=manager)
        assert notif.status == Notification.Status.PENDING
        assert notif.sent_at is None

    def test_notification_status_choices(self):
        assert Notification.Status.PENDING == "PENDING"
        assert Notification.Status.SENT == "SENT"
        assert Notification.Status.FAILED == "FAILED"


# ---------------------------------------------------------------------------
# Celery Task Enqueued
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestNotificationTaskEnqueued:
    @pytest.mark.parametrize(
        "notif_type",
        [
            Notification.Type.TICKET_ASSIGNED,
            Notification.Type.STATUS_CHANGED,
            Notification.Type.PRIORITY_CHANGED,
            Notification.Type.TICKET_UPDATED,
            Notification.Type.COMMENT_ADDED,
        ],
    )
    def test_task_enqueued_on_notification_creation(self, manager, notif_type):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=manager)
        with patch("apps.notifications.tasks.send_notification_email.delay") as mock_delay:
            from apps.notifications.services import create_notification

            create_notification(ticket=ticket, user=manager, type=notif_type)
            mock_delay.assert_called_once()
            call_kwargs = mock_delay.call_args[1]
            assert "notification_id" in call_kwargs
            assert "recipient_email" in call_kwargs
            assert call_kwargs["notification_type"] == notif_type
            assert call_kwargs["ticket_id"] == str(ticket.id)
            assert call_kwargs["ticket_title"] == ticket.title

    def test_task_receives_only_primitives(self, manager):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=manager)
        with patch("apps.notifications.tasks.send_notification_email.delay") as mock_delay:
            from apps.notifications.services import create_notification

            create_notification(ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED)
            call_kwargs = mock_delay.call_args[1]
            for value in call_kwargs.values():
                assert isinstance(value, str | int | float | bool | type(None))


# ---------------------------------------------------------------------------
# Celery Task — Email Sending
# ---------------------------------------------------------------------------


class TestSendNotificationEmailTask:
    def test_task_sends_email_successfully(self, manager):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED
        )

        with patch("apps.notifications.tasks.mail.EmailMultiAlternatives") as mock_email_cls:
            mock_email_instance = mock_email_cls.return_value
            from apps.notifications.tasks import send_notification_email

            send_notification_email(
                notification_id=str(notif.id),
                recipient_name=manager.first_name or manager.email,
                recipient_email=manager.email,
                notification_type=Notification.Type.TICKET_ASSIGNED,
                ticket_id=str(ticket.id),
                ticket_title=ticket.title,
                ticket_priority=ticket.priority,
                ticket_status=ticket.status,
            )
            mock_email_cls.assert_called_once()
            mock_email_instance.send.assert_called_once()
            call_kwargs = mock_email_cls.call_args[1]
            assert "assigned a ticket" in call_kwargs["subject"]
            assert manager.email in call_kwargs["to"]

    def test_notification_becomes_sent_on_success(self, manager):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED
        )

        with patch("apps.notifications.tasks.mail.EmailMultiAlternatives"):
            from apps.notifications.tasks import send_notification_email

            send_notification_email(
                notification_id=str(notif.id),
                recipient_name=manager.first_name or manager.email,
                recipient_email=manager.email,
                notification_type=Notification.Type.TICKET_ASSIGNED,
                ticket_id=str(ticket.id),
                ticket_title=ticket.title,
                ticket_priority=ticket.priority,
                ticket_status=ticket.status,
            )
            notif.refresh_from_db()
            assert notif.status == Notification.Status.SENT
            assert notif.sent_at is not None

    def test_notification_becomes_failed_on_exception(self, manager):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED
        )

        with patch(
            "apps.notifications.tasks.mail.EmailMultiAlternatives",
            side_effect=Exception("SMTP error"),
        ):
            from apps.notifications.tasks import send_notification_email

            with pytest.raises(Exception, match="SMTP error"):
                send_notification_email(
                    notification_id=str(notif.id),
                    recipient_name=manager.first_name or manager.email,
                    recipient_email=manager.email,
                    notification_type=Notification.Type.TICKET_ASSIGNED,
                    ticket_id=str(ticket.id),
                    ticket_title=ticket.title,
                    ticket_priority=ticket.priority,
                    ticket_status=ticket.status,
                )
            notif.refresh_from_db()
            assert notif.status == Notification.Status.FAILED
            assert notif.sent_at is None

    def test_task_handles_notification_not_found(self):
        import uuid
        from unittest.mock import patch

        with patch("apps.notifications.tasks.mail.EmailMultiAlternatives") as mock_email_cls:
            from apps.notifications.tasks import send_notification_email

            send_notification_email(
                notification_id=str(uuid.uuid4()),
                recipient_name="Test User",
                recipient_email="test@example.com",
                notification_type=Notification.Type.TICKET_ASSIGNED,
                ticket_id=str(uuid.uuid4()),
                ticket_title="Test Ticket",
                ticket_priority="MEDIUM",
                ticket_status="OPEN",
            )
            mock_email_cls.assert_not_called()

    def test_task_sends_correct_email_content(self, agent):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=agent, title="Fix login bug")
        notif = NotificationFactory(ticket=ticket, user=agent, type=Notification.Type.COMMENT_ADDED)

        with patch("apps.notifications.tasks.mail.EmailMultiAlternatives") as mock_email_cls:
            from apps.notifications.tasks import send_notification_email

            send_notification_email(
                notification_id=str(notif.id),
                recipient_name=agent.first_name or agent.email,
                recipient_email=agent.email,
                notification_type=Notification.Type.COMMENT_ADDED,
                ticket_id=str(ticket.id),
                ticket_title=ticket.title,
                ticket_priority=ticket.priority,
                ticket_status=ticket.status,
            )
            call_kwargs = mock_email_cls.call_args[1]
            subject = call_kwargs["subject"]
            body = call_kwargs["body"]
            assert "comment on ticket" in subject
            assert "Fix login bug" in body
            assert "received a new comment" in body

    def test_task_includes_threading_headers(self, agent):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=agent, title="Fix login bug")
        notif = NotificationFactory(
            ticket=ticket, user=agent, type=Notification.Type.TICKET_ASSIGNED
        )

        with patch("apps.notifications.tasks.mail.EmailMultiAlternatives") as mock_email_cls:
            from apps.notifications.tasks import send_notification_email

            send_notification_email(
                notification_id=str(notif.id),
                recipient_name=agent.first_name or agent.email,
                recipient_email=agent.email,
                notification_type=Notification.Type.TICKET_ASSIGNED,
                ticket_id=str(ticket.id),
                ticket_title=ticket.title,
                ticket_priority=ticket.priority,
                ticket_status=ticket.status,
            )
            call_kwargs = mock_email_cls.call_args[1]
            headers = call_kwargs["headers"]
            assert "In-Reply-To" in headers
            assert "References" in headers
            assert str(ticket.id) in headers["In-Reply-To"]


# ---------------------------------------------------------------------------
# Celery Task — Retry Behavior
# ---------------------------------------------------------------------------


class TestNotificationTaskRetry:
    def test_task_retries_on_exception(self, manager):
        from unittest.mock import patch

        ticket = TicketFactory(created_by=manager)
        notif = NotificationFactory(
            ticket=ticket, user=manager, type=Notification.Type.TICKET_ASSIGNED
        )

        with patch(
            "apps.notifications.tasks.mail.EmailMultiAlternatives",
            side_effect=Exception("Temporary failure"),
        ):
            from apps.notifications.tasks import send_notification_email

            with patch.object(
                send_notification_email, "retry", side_effect=celery.exceptions.Retry()
            ) as mock_retry:
                send_notification_email.apply(
                    kwargs={
                        "notification_id": str(notif.id),
                        "recipient_name": manager.first_name or manager.email,
                        "recipient_email": manager.email,
                        "notification_type": Notification.Type.TICKET_ASSIGNED,
                        "ticket_id": str(ticket.id),
                        "ticket_title": ticket.title,
                        "ticket_priority": ticket.priority,
                        "ticket_status": ticket.status,
                    },
                )
                mock_retry.assert_called_once()

    def test_task_has_retry_configuration(self):
        from apps.notifications.tasks import send_notification_email

        assert send_notification_email.max_retries == 3
        assert send_notification_email.default_retry_delay == 60
        assert send_notification_email.autoretry_for == (Exception,)


# ---------------------------------------------------------------------------
# Transaction Safety — on_commit
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestTransactionSafety:
    def test_task_dispatched_on_successful_commit(self, manager):
        """When the transaction commits, send_notification_email.delay is called."""
        from unittest.mock import patch

        from django.db import transaction

        from apps.notifications.services import create_notification

        ticket = TicketFactory(created_by=manager)

        with patch("apps.notifications.services.send_notification_email.delay") as mock_delay:
            with transaction.atomic():
                create_notification(
                    ticket=ticket,
                    user=manager,
                    type=Notification.Type.TICKET_ASSIGNED,
                )
            mock_delay.assert_called_once()

    def test_no_task_dispatched_on_rollback(self, manager):
        """When the transaction rolls back, no Celery task is dispatched."""
        from unittest.mock import patch

        from django.db import transaction
        from django.db.utils import IntegrityError

        from apps.notifications.services import create_notification

        ticket = TicketFactory(created_by=manager)

        with patch("apps.notifications.services.send_notification_email.delay") as mock_delay:
            try:
                with transaction.atomic():
                    create_notification(
                        ticket=ticket,
                        user=manager,
                        type=Notification.Type.TICKET_ASSIGNED,
                    )
                    raise IntegrityError("simulated rollback")
            except IntegrityError:
                pass

            mock_delay.assert_not_called()

    def test_no_notification_persisted_on_rollback(self, manager):
        """When the transaction rolls back, the notification row is gone."""
        from unittest.mock import patch

        from django.db import transaction
        from django.db.utils import IntegrityError

        from apps.notifications.services import create_notification

        ticket = TicketFactory(created_by=manager)
        initial_count = Notification.objects.count()

        with patch("apps.notifications.services.send_notification_email.delay"):
            try:
                with transaction.atomic():
                    create_notification(
                        ticket=ticket,
                        user=manager,
                        type=Notification.Type.TICKET_ASSIGNED,
                    )
                    raise IntegrityError("simulated rollback")
            except IntegrityError:
                pass

        assert Notification.objects.count() == initial_count
