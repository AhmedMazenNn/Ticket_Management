"""Reusable email builder for notification emails."""

from django.conf import settings

EMAIL_SUBJECTS = {
    "TICKET_ASSIGNED": "Ticket Assigned",
    "STATUS_CHANGED": "Ticket Status Changed",
    "PRIORITY_CHANGED": "Ticket Priority Changed",
    "TICKET_UPDATED": "Ticket Updated",
    "COMMENT_ADDED": "New Comment on Ticket",
}


def build_notification_email(
    *,
    recipient_email: str,
    notification_type: str,
    ticket_id: str,
    ticket_title: str,
) -> dict:
    """Build email content for a notification.

    Returns a dict with subject, message, from_email, recipient_list,
    and headers for threading emails about the same ticket.
    """
    subject = EMAIL_SUBJECTS.get(notification_type, "Ticket Notification")
    readable_type = notification_type.replace("_", " ").title()
    message = (
        f"Hello,\n\n"
        f"You have a new notification: {readable_type}\n\n"
        f"Ticket: {ticket_title}\n"
        f"Ticket ID: {ticket_id}\n\n"
        f"Regards,\n"
        f"Ticket Management Team"
    )

    message_id = f"ticket-{ticket_id}@ticketapp.local"
    headers = {
        "In-Reply-To": message_id,
        "References": message_id,
    }

    return {
        "subject": f"[Ticket {ticket_title}] {subject}",
        "message": message,
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "recipient_list": [recipient_email],
        "headers": headers,
    }
