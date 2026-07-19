"""Reusable email builder for notification emails."""

from django.conf import settings
from django.utils.html import escape

EMAIL_SUBJECTS = {
    "TICKET_ASSIGNED": "You've been assigned a ticket",
    "STATUS_CHANGED": "Ticket status updated",
    "PRIORITY_CHANGED": "Ticket priority changed",
    "TICKET_UPDATED": "Ticket updated",
    "COMMENT_ADDED": "New comment on ticket",
}

EMAIL_ACTION_LABELS = {
    "TICKET_ASSIGNED": "assigned to you",
    "STATUS_CHANGED": "had its status changed",
    "PRIORITY_CHANGED": "had its priority changed",
    "TICKET_UPDATED": "was updated",
    "COMMENT_ADDED": "received a new comment",
}

PRIORITY_COLORS = {
    "LOW": "#10b981",
    "MEDIUM": "#f59e0b",
    "HIGH": "#ef4444",
}

STATUS_COLORS = {
    "OPEN": "#4f46e5",
    "IN_PROGRESS": "#f59e0b",
    "CLOSED": "#10b981",
}


def _build_html(
    *,
    recipient_name: str,
    notification_type: str,
    ticket_id: str,
    ticket_title: str,
    ticket_priority: str,
    ticket_status: str,
    triggered_by: str,
    description: str,
) -> str:
    action_label = EMAIL_ACTION_LABELS.get(notification_type, "received an update")
    priority_color = PRIORITY_COLORS.get(ticket_priority, "#64748b")
    status_color = STATUS_COLORS.get(ticket_status, "#64748b")
    frontend_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    ticket_url = f"{frontend_base}/tickets/{ticket_id}"
    year = __import__("datetime").datetime.now().year

    description_block = ""
    if description:
        truncated = description[:200] + ("..." if len(description) > 200 else "")
        description_block = f"""
                <tr>
                  <td style="padding:16px 24px 0;">
                    <p style="margin:0;font-size:13px;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">Description</p>
                    <p style="margin:8px 0 0;font-size:14px;color:#475569;line-height:1.6;background:#f8fafc;border-left:3px solid #e2e8f0;padding:12px 16px;border-radius:0 8px 8px 0;">{escape(truncated)}</p>
                  </td>
                </tr>"""

    triggered_by_block = ""
    if triggered_by:
        triggered_by_block = f"""
                <tr>
                  <td style="padding:16px 24px 0;">
                    <p style="margin:0;font-size:13px;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">Triggered by</p>
                    <p style="margin:8px 0 0;font-size:14px;color:#1e293b;font-weight:500;">{escape(triggered_by)}</p>
                  </td>
                </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;">

          <!-- Logo -->
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#6366f1,#9333ea);border-radius:12px;padding:10px 14px;">
                    <span style="font-size:18px;font-weight:900;color:#ffffff;letter-spacing:-0.02em;">T</span>
                  </td>
                  <td style="padding-left:12px;">
                    <span style="font-size:20px;font-weight:700;color:#1e293b;letter-spacing:-0.02em;">TicketFlow</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08),0 4px 12px rgba(0,0,0,0.04);">

              <!-- Header bar -->
              <tr>
                <td style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:24px;">
                  <p style="margin:0;font-size:13px;color:rgba(255,255,255,0.75);text-transform:uppercase;letter-spacing:0.08em;font-weight:600;">Notification</p>
                  <p style="margin:6px 0 0;font-size:20px;font-weight:700;color:#ffffff;line-height:1.3;">Ticket {action_label}</p>
                </td>
              </tr>

              <!-- Greeting -->
              <tr>
                <td style="padding:24px 24px 0;">
                  <p style="margin:0;font-size:15px;color:#334155;">Hi {escape(recipient_name)},</p>
                  <p style="margin:8px 0 0;font-size:14px;color:#64748b;line-height:1.6;">
                    A ticket has {action_label}. Here are the details:
                  </p>
                </td>
              </tr>

              <!-- Ticket info -->
              <tr>
                <td style="padding:20px 24px 0;">
                  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;">
                    <tr>
                      <td style="padding:20px;">
                        <!-- Title -->
                        <p style="margin:0;font-size:13px;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">Ticket</p>
                        <p style="margin:6px 0 0;font-size:16px;font-weight:700;color:#1e293b;line-height:1.4;">
                          <a href="{ticket_url}" style="color:#4f46e5;text-decoration:none;">{escape(ticket_title)}</a>
                        </p>

                        <!-- Meta row -->
                        <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;">
                          <tr>
                            <td width="33%" valign="top">
                              <p style="margin:0;font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">Priority</p>
                              <p style="margin:4px 0 0;">
                                <span style="display:inline-block;font-size:12px;font-weight:600;color:{priority_color};background:{priority_color}15;padding:3px 10px;border-radius:20px;border:1px solid {priority_color}30;">{ticket_priority.title()}</span>
                              </p>
                            </td>
                            <td width="33%" valign="top">
                              <p style="margin:0;font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">Status</p>
                              <p style="margin:4px 0 0;">
                                <span style="display:inline-block;font-size:12px;font-weight:600;color:{status_color};background:{status_color}15;padding:3px 10px;border-radius:20px;border:1px solid {status_color}30;">{ticket_status.replace("_", " ").title()}</span>
                              </p>
                            </td>
                            <td width="33%" valign="top">
                              <p style="margin:0;font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;">ID</p>
                              <p style="margin:4px 0 0;font-size:12px;color:#64748b;font-family:monospace;">{ticket_id[:8]}</p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              {triggered_by_block}
              {description_block}

              <!-- CTA Button -->
              <tr>
                <td style="padding:24px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td align="center">
                        <a href="{ticket_url}" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:10px;box-shadow:0 2px 8px rgba(99,102,241,0.35);">
                          View Ticket &rarr;
                        </a>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding:24px 16px;">
              <p style="margin:0;font-size:12px;color:#94a3b8;line-height:1.6;">
                You received this because you're a member of this workspace.<br>
                <a href="{frontend_base}/settings" style="color:#6366f1;text-decoration:none;">Manage notification settings</a>
              </p>
              <p style="margin:12px 0 0;font-size:11px;color:#cbd5e1;">&copy; {year} TicketFlow. All rights reserved.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _build_plain_text(
    *,
    notification_type: str,
    ticket_id: str,
    ticket_title: str,
    ticket_priority: str,
    ticket_status: str,
    triggered_by: str,
    description: str,
) -> str:
    action_label = EMAIL_ACTION_LABELS.get(notification_type, "received an update")
    frontend_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    ticket_url = f"{frontend_base}/tickets/{ticket_id}"

    lines = [
        f"Ticket {action_label}",
        "",
        f"Ticket:  {ticket_title}",
        f"ID:      {ticket_id[:8]}",
        f"Priority: {ticket_priority.title()}",
        f"Status:  {ticket_status.replace('_', ' ').title()}",
    ]

    if triggered_by:
        lines.append(f"Triggered by: {triggered_by}")

    if description:
        truncated = description[:200] + ("..." if len(description) > 200 else "")
        lines.extend(["", "Description:", truncated])

    lines.extend(
        [
            "",
            f"View ticket: {ticket_url}",
            "",
            "---",
            "You received this because you're a member of this workspace.",
            f"Manage notifications: {frontend_base}/settings",
        ]
    )

    return "\n".join(lines)


def build_notification_email(
    *,
    recipient_name: str,
    recipient_email: str,
    notification_type: str,
    ticket_id: str,
    ticket_title: str,
    ticket_priority: str,
    ticket_status: str,
    triggered_by: str = "",
    description: str = "",
) -> dict:
    """Build email content for a notification.

    Returns a dict with subject, html, plain message, from_email,
    recipient_list, and headers for threading emails about the same ticket.
    """
    subject = EMAIL_SUBJECTS.get(notification_type, "Ticket Notification")

    html = _build_html(
        recipient_name=recipient_name,
        notification_type=notification_type,
        ticket_id=ticket_id,
        ticket_title=ticket_title,
        ticket_priority=ticket_priority,
        ticket_status=ticket_status,
        triggered_by=triggered_by,
        description=description,
    )

    message = _build_plain_text(
        notification_type=notification_type,
        ticket_id=ticket_id,
        ticket_title=ticket_title,
        ticket_priority=ticket_priority,
        ticket_status=ticket_status,
        triggered_by=triggered_by,
        description=description,
    )

    message_id = f"ticket-{ticket_id}@ticketapp.local"
    headers = {
        "In-Reply-To": message_id,
        "References": message_id,
    }

    return {
        "subject": f"[TicketFlow] {subject}: {ticket_title}",
        "message": message,
        "html": html,
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "recipient_list": [recipient_email],
        "headers": headers,
    }
