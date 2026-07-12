"""RabbitMQ event publisher."""

from __future__ import annotations

import json
import logging

import pika

from .connection import get_connection
from .constants import EXCHANGE

logger = logging.getLogger(__name__)


def publish_event(routing_key: str, payload: dict) -> bool:
    """Publish an event to the RabbitMQ topic exchange.

    Args:
        routing_key: The routing key (e.g. "ticket.created").
        payload: The event payload dict (must be JSON-serializable).

    Returns:
        True if the event was published, False otherwise.
    """
    connection = get_connection()
    if connection is None:
        return False

    try:
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(payload, default=str).encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info("Published event: %s", routing_key)
        return True
    except Exception:
        logger.exception("Failed to publish event: %s", routing_key)
        return False
    finally:
        try:
            connection.close()
        except Exception:
            pass
