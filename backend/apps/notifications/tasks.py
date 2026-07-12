"""Celery tasks for notification email processing."""

import logging

from celery import shared_task
from django.core import mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_notification_email(
    self,
    notification_id: str,
    recipient_email: str,
    notification_type: str,
    ticket_id: str,
    ticket_title: str,
):
    """Send notification email asynchronously.

    Retries automatically on failure with exponential backoff.
    Updates notification status to SENT or FAILED.
    """
    from apps.notifications.email import build_notification_email
    from apps.notifications.models import Notification

    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error("Notification %s not found, skipping email.", notification_id)
        return

    email_data = build_notification_email(
        recipient_email=recipient_email,
        notification_type=notification_type,
        ticket_id=ticket_id,
        ticket_title=ticket_title,
    )

    try:
        mail.send_mail(
            email_data["subject"],
            email_data["message"],
            email_data["from_email"],
            email_data["recipient_list"],
        )
        notification.status = Notification.Status.SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=["status", "sent_at"])
        logger.info("Email sent for notification %s to %s.", notification_id, recipient_email)
    except Exception:
        notification.status = Notification.Status.FAILED
        notification.save(update_fields=["status"])
        logger.exception(
            "Failed to send email for notification %s to %s.",
            notification_id,
            recipient_email,
        )
        raise
