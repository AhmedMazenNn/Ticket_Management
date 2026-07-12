"""Reusable email builder for notification emails."""

EMAIL_SUBJECTS = {
    "TICKET_ASSIGNED": "Ticket Assigned",
    "STATUS_CHANGED": "Ticket Status Changed",
    "PRIORITY_CHANGED": "Ticket Priority Changed",
    "TICKET_UPDATED": "Ticket Updated",
    "COMMENT_ADDED": "New Comment on Ticket",
}

DEFAULT_FROM_EMAIL = "noreply@ticketapp.local"


def build_notification_email(
    *,
    recipient_email: str,
    notification_type: str,
    ticket_id: str,
    ticket_title: str,
) -> dict:
    """Build email content for a notification.

    Returns a dict with subject, message, from_email, recipient_list.
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
    return {
        "subject": subject,
        "message": message,
        "from_email": DEFAULT_FROM_EMAIL,
        "recipient_list": [recipient_email],
    }
