"""RabbitMQ exchange and routing key constants."""

EXCHANGE = "ticket_events"


class RoutingKey:
    TICKET_CREATED = "ticket.created"
    TICKET_UPDATED = "ticket.updated"
    TICKET_ASSIGNED = "ticket.assigned"
    TICKET_STATUS_CHANGED = "ticket.status_changed"
    TICKET_PRIORITY_CHANGED = "ticket.priority_changed"
    COMMENT_CREATED = "comment.created"
