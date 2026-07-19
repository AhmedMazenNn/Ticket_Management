"""Tests for RabbitMQ messaging integration."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from apps.accounts.factories import UserFactory
from apps.accounts.models import User
from apps.tickets.factories import TicketFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def manager():
    return UserFactory(role=User.Role.MANAGER)


@pytest.fixture
def agent():
    return UserFactory(role=User.Role.AGENT)


# ---------------------------------------------------------------------------
# Publisher — Unit Tests
# ---------------------------------------------------------------------------


class TestPublishEvent:
    @patch("apps.messaging.publisher.get_connection")
    def test_publish_event_serializes_json(self, mock_get_conn):
        from apps.messaging.publisher import publish_event

        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_get_conn.return_value = mock_conn

        payload = {
            "event": "ticket.created",
            "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2026-07-12T20:00:00+00:00",
        }
        result = publish_event("ticket.created", payload)

        assert result is True
        call_args = mock_channel.basic_publish.call_args
        body = json.loads(call_args[1]["body"])
        assert body["event"] == "ticket.created"
        assert body["ticket_id"] == "550e8400-e29b-41d4-a716-446655440000"

    @patch("apps.messaging.publisher.get_connection")
    def test_publish_event_connects_and_publishes(self, mock_get_conn):
        from apps.messaging.publisher import publish_event

        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_conn.channel.return_value = mock_channel
        mock_get_conn.return_value = mock_conn

        publish_event("ticket.created", {"event": "ticket.created"})

        mock_get_conn.assert_called_once()
        mock_channel.exchange_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("apps.messaging.publisher.get_connection")
    def test_publish_event_failure_does_not_raise(self, mock_get_conn):
        from apps.messaging.publisher import publish_event

        mock_get_conn.return_value = None

        result = publish_event("ticket.created", {"event": "ticket.created"})
        assert result is False

    @patch("apps.messaging.publisher.get_connection")
    def test_publish_event_channel_error_does_not_raise(self, mock_get_conn):
        from apps.messaging.publisher import publish_event

        mock_conn = MagicMock()
        mock_conn.channel.side_effect = Exception("channel error")
        mock_get_conn.return_value = mock_conn

        result = publish_event("ticket.created", {"event": "ticket.created"})
        assert result is False


# ---------------------------------------------------------------------------
# Integration — Ticket Events
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestTicketEventPublishing:
    @patch("apps.tickets.services.publish_event")
    def test_ticket_created_publishes_event(self, mock_publish, manager):
        from apps.tickets.services import create_ticket

        ticket = create_ticket(title="New Ticket", created_by=manager)

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "ticket.created"
        payload = call_args[0][1]
        assert payload["event"] == "ticket.created"
        assert payload["ticket_id"] == str(ticket.id)
        assert payload["created_by"] == str(manager.id)

    @patch("apps.tickets.services.publish_event")
    def test_ticket_status_change_publishes_event(self, mock_publish, manager):
        from apps.tickets.services import update_ticket

        ticket = TicketFactory(created_by=manager)
        update_ticket(ticket, changed_by=manager, status="IN_PROGRESS")

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "ticket.status_changed"
        payload = call_args[0][1]
        assert payload["event"] == "ticket.status_changed"

    @patch("apps.tickets.services.publish_event")
    def test_ticket_priority_change_publishes_event(self, mock_publish, manager):
        from apps.tickets.services import update_ticket

        ticket = TicketFactory(created_by=manager)
        update_ticket(ticket, changed_by=manager, priority="HIGH")

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "ticket.priority_changed"
        payload = call_args[0][1]
        assert payload["event"] == "ticket.priority_changed"

    @patch("apps.tickets.services.publish_event")
    def test_ticket_update_publishes_event(self, mock_publish, manager):
        from apps.tickets.services import update_ticket

        ticket = TicketFactory(created_by=manager)
        update_ticket(ticket, changed_by=manager, title="Updated Title")

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "ticket.updated"
        payload = call_args[0][1]
        assert payload["event"] == "ticket.updated"

    @patch("apps.tickets.services.publish_event")
    def test_ticket_assignment_publishes_event(self, mock_publish, manager, agent):
        from apps.tickets.services import assign_ticket

        ticket = TicketFactory(created_by=manager)
        assign_ticket(ticket, agent, changed_by=manager)

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "ticket.assigned"
        payload = call_args[0][1]
        assert payload["event"] == "ticket.assigned"
        assert payload["assigned_to"] == str(agent.id)


# ---------------------------------------------------------------------------
# Integration — Comment Events
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
class TestCommentEventPublishing:
    @patch("apps.comments.services.publish_event")
    def test_comment_created_publishes_event(self, mock_publish, manager):
        from apps.comments.services import create_comment

        ticket = TicketFactory(created_by=manager)
        comment = create_comment(ticket=ticket, author=manager, body="Test comment")

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "comment.created"
        payload = call_args[0][1]
        assert payload["event"] == "comment.created"
        assert payload["comment_id"] == str(comment.id)
        assert payload["ticket_id"] == str(ticket.id)
        assert payload["author"] == str(manager.id)


# ---------------------------------------------------------------------------
# Consumer
# ---------------------------------------------------------------------------


class TestConsumer:
    def test_callback_parses_json(self):
        from apps.messaging.consumer import _callback

        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = json.dumps({"event": "ticket.created", "ticket_id": "123"}).encode()

        _callback(ch, method, properties, body)

    def test_callback_handles_invalid_json(self):
        from apps.messaging.consumer import _callback

        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = b"not json"

        _callback(ch, method, properties, body)
