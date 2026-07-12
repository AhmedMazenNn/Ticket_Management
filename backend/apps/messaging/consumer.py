"""Simple RabbitMQ consumer for debugging and verification."""

from __future__ import annotations

import json
import logging
import signal
import sys

import pika

from .connection import get_connection_params
from .constants import EXCHANGE

logger = logging.getLogger(__name__)


def _callback(ch, method, properties, body):
    """Handle incoming messages."""
    try:
        payload = json.loads(body)
        event = payload.get("event", "unknown")
        logger.info("Received: %s", event)
        for key, value in payload.items():
            logger.info("  %s: %s", key, value)
    except json.JSONDecodeError:
        logger.error("Failed to decode message: %s", body)


def consume():
    """Start consuming events from the ticket_events exchange."""
    connection = pika.BlockingConnection(get_connection_params())
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key="#")

    logger.info("Waiting for events. Press Ctrl+C to exit.")
    channel.basic_consume(queue=queue_name, on_message_callback=_callback, auto_ack=True)

    def _shutdown(signum, frame):
        logger.info("Shutting down consumer.")
        channel.stop_consuming()
        connection.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    channel.start_consuming()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consume()
