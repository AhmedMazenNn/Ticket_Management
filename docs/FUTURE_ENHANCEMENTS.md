# Future Enhancements

This document outlines planned and potential improvements for the Ticket Management App.

---

## 1. Google OAuth Authentication

**Priority:** High

Allow users to sign in with their Google account instead of email/password.

### Requirements
- Integrate `django-allauth` with Google OAuth2 provider
- Add Google client ID/secret to environment variables
- Frontend: add "Sign in with Google" button on login and register pages
- Handle account linking if a user already exists with the same email
- Store OAuth tokens for potential Google API integrations (Calendar, etc.)

### Considerations
- Migrate existing password-based users to support both auth methods
- Add account settings page to link/unlink Google account
- Handle token refresh for long-lived sessions

---

## 2. Notification Preferences

**Priority:** High

Let users control which notifications they receive and how (in-app, email, both).

### Requirements
- Add `NotificationPreference` model per user with per-type toggles:
  - `ticket_assigned`: in_app, email
  - `status_changed`: in_app, email
  - `priority_changed`: in_app, email
  - `ticket_updated`: in_app, email
  - `comment_added`: in_app, email
- Settings page: add notification preferences section
- Backend: check preferences before creating notifications and sending emails
- Default: all notifications enabled

### Considerations
- Add a global "quiet hours" setting (no emails during off-hours)
- Per-ticket notification mute option
-.digest email option (daily/weekly summary instead of individual emails)

---

## 3. Grouped Notifications

**Priority:** Medium

Group related notifications together to reduce noise.

### Requirements
- Group consecutive notifications of the same type on the same ticket
  - e.g., "Status changed 3 times on Ticket X" instead of 3 separate notifications
- Backend: aggregate group count and latest timestamp
- Frontend: display grouped notifications with expandable detail
- Notification preferences: toggle between grouped and individual mode

### Considerations
- Grouping window: group notifications within a configurable time window (e.g., 5 minutes)
- Keep high-priority notifications (ticket assigned) ungrouped
- Grouped notifications should still respect read/unread state per individual

---

## 4. Ticket Grouping / Categories

**Priority:** Medium

Organize tickets into logical groups beyond just status and priority.

### Requirements
- Add `Tag` model with name, color, and workspace scope
- Add `Ticket.tags` many-to-many field
- Create/edit ticket UI: tag selector with autocomplete
- Filter tickets by tags on the tickets list page
- Dashboard: tag-based breakdown chart

### Considerations
- Tags are optional — tickets can have zero or many
- Tag management page for admins (create, edit, delete tags)
- Tag-based notification routing (notify team leads when a "bug" tag is added)
- Consider also adding `Category` as a single-select field for broader grouping (e.g., "Bug", "Feature", "Support")

---

## 5. File Attachments

**Priority:** Medium

Allow users to attach files to tickets and comments.

### Requirements
- Add `TicketAttachment` and `CommentAttachment` models
- File upload via drag-and-drop or file picker
- Support common formats: images, PDFs, text files, zip archives
- File size limit (e.g., 10MB per file)
- Store files in local media storage (S3-compatible for production)
- Thumbnail generation for images
- Attachments visible in ticket detail and comment threads

### Considerations
- Virus/malware scanning on upload
- Storage quota per workspace
- File access control (only workspace members can view/download)

---

## 6. SLA & Due Dates

**Priority:** Medium

Track service level agreements and ticket deadlines.

### Requirements
- Add `due_date` field to Ticket model
- Add `SLA` model (name, response time, resolution time, applies to priority)
- Auto-assign due dates based on SLA rules when ticket is created
- Dashboard widget: overdue tickets count and list
- Email reminders: notify assignee 24h and 1h before due date
- Escalation: reassign or notify manager when SLA is breached

### Considerations
- SLA calculation should exclude weekends/holidays (configurable)
- Pause SLA timer when ticket status is "On Hold"
- SLA reporting and analytics page

---

## 7. Internal Notes

**Priority:** Low

Private notes on tickets visible only to specific roles.

### Requirements
- Add `Note` model tied to a ticket
- Notes are internal — not visible to the ticket creator if they are an agent
- Only Admins and Managers can see all notes
- Agents can see notes added by other agents on their assigned tickets
- UI: separate tab or section in ticket detail

### Considerations
- Notes should appear in the activity timeline
- Notes should be searchable
- Notes should not trigger email notifications

---

## 8. Saved Views / Custom Filters

**Priority:** Low

Let users save custom ticket filters for quick access.

### Requirements
- Add `SavedView` model (name, filters JSON, user FK)
- UI: "Save this view" button on the tickets list page
- Sidebar or dropdown: quick access to saved views
- Default views: "My Open Tickets", "High Priority", "Recently Updated"
- Share views with the workspace (optional)

### Considerations
- Views should update in real-time as new tickets match the filters
- Limit number of saved views per user (e.g., 20)
- Consider making some views workspace-wide (admin-created)

---

## 9. Two-Factor Authentication (2FA)

**Priority:** Low

Add an extra layer of security for user accounts.

### Requirements
- TOTP-based 2FA (Google Authenticator, Authy, etc.)
- Setup flow: QR code + backup codes
- Login flow: password + TOTP code
- Account settings: enable/disable 2FA, regenerate backup codes
- Admin can require 2FA for all workspace members

### Considerations
- Backup codes for account recovery
- Trusted devices (remember for 30 days)
- Recovery email flow if user loses access to TOTP device

---

## 10. Webhooks & Integrations

**Priority:** Low

Connect TicketFlow to external tools via webhooks and integrations.

### Requirements
- Outgoing webhooks: POST to a configured URL on ticket events
- Webhook management page for admins (create, edit, test, delete)
- Payload includes event type, ticket data, and user info
- Retry failed webhook deliveries with exponential backoff
- Webhook logs for debugging

### Considerations
- Optional integrations: Slack, Microsoft Teams, Jira
- Incoming webhooks: create tickets from external systems
- Webhook signing for security (HMAC signature verification)
- Rate limiting to prevent abuse

---

## 11. Reporting & Analytics

**Priority:** Low

Provide insights into team performance and ticket trends.

### Requirements
- Reports page with charts:
  - Tickets created vs resolved over time
  - Average resolution time by priority
  - Agent workload distribution
  - Ticket volume by day/week/month
- Export reports as CSV or PDF
- Date range selector for all reports
- Role-based access: Admins see all, Managers see team, Agents see own

### Considerations
- Cache report queries for performance
- Scheduled report emails (weekly summary to managers)
- Comparison periods (this week vs last week)

---

## 12. Keyboard Shortcuts

**Priority:** Low

Power-user shortcuts for faster navigation.

### Requirements
- `?` — open shortcuts panel
- `g d` — go to dashboard
- `g t` — go to tickets
- `n` — create new ticket
- `/` — focus search bar
- `Esc` — close modals/panels
- Arrow keys — navigate ticket lists

### Considerations
- Configurable key bindings
- Disable shortcuts when typing in input fields
- Show shortcuts hint on relevant pages

---

## Priority Summary

| Priority | Enhancements |
|----------|-------------|
| High | Google OAuth, Notification Preferences |
| Medium | Grouped Notifications, Ticket Grouping, File Attachments, SLA & Due Dates |
| Low | Internal Notes, Saved Views, 2FA, Webhooks, Reporting, Keyboard Shortcuts |
