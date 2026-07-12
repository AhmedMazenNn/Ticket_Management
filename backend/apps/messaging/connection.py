"""RabbitMQ connection manager."""

from __future__ import annotations

import logging

import pika
from decouple import config

logger = logging.getLogger(__name__)


def get_connection_params() -> pika.ConnectionParameters:
    """Build connection parameters from environment variables."""
    return pika.ConnectionParameters(
        host=config("RABBITMQ_HOST", default="localhost"),
        port=config("RABBITMQ_PORT", default=5672, cast=int),
        virtual_host=config("RABBITMQ_VHOST", default="/"),
        credentials=pika.PlainCredentials(
            config("RABBITMQ_USERNAME", default="guest"),
            config("RABBITMQ_PASSWORD", default="guest"),
        ),
    )


def get_connection() -> pika.BlockingConnection | None:
    """Create a blocking connection to RabbitMQ.

    Returns None if the connection fails.
    """
    try:
        return pika.BlockingConnection(get_connection_params())
    except pika.exceptions.AMQPConnectionError:
        logger.exception("Failed to connect to RabbitMQ.")
        return None
