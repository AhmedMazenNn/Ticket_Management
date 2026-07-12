import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.comments.models import Comment
from apps.comments.services import create_comment
from apps.tickets.models import Ticket
from apps.tickets.services import assign_ticket, create_ticket, update_ticket

User = get_user_model()

TITLES = [
    "Fix login page redirect bug",
    "Update API documentation",
    "Database migration review",
    "Add email notifications",
    "Fix dashboard chart rendering",
    "Optimize ticket list query",
    "Add ticket export to CSV",
    "Fix pagination on mobile",
    "Implement comment editing",
    "Add role-based filtering",
    "Fix timezone display",
    "Add ticket priority sorting",
    "Review security headers",
    "Add dark mode support",
    "Fix CSV import encoding",
    "Resolve WebSocket connection drops",
    "Add audit log viewer for admins",
    "Implement ticket SLA tracking",
    "Fix broken image uploads on Safari",
    "Add two-factor authentication",
    "Migrate from REST to GraphQL",
    "Fix double-submit on ticket form",
    "Add keyboard shortcuts",
    "Refactor notification service",
    "Fix memory leak in long-polling",
]

DESCRIPTIONS = [
    "Users are redirected to a 404 page after successful login on Chrome.",
    "The Swagger docs need to be updated with the new comments endpoints.",
    "Review the latest migration files before deploying to production.",
    "Send email when a ticket is assigned to an agent.",
    "Doughnut chart shows blank on Safari browsers.",
    "The ticket list endpoint is slow with 10k+ records.",
    "Managers need to export ticket data for reporting.",
    "Page numbers overlap on small screens.",
    "Users should be able to edit their own comments.",
    "Allow filtering tickets by assignee role.",
    "Timestamps show UTC instead of user's local timezone.",
    "Allow sorting tickets by priority in the list view.",
    "Ensure all security headers are properly configured.",
    "Implement a dark mode toggle in the settings page.",
    "UTF-8 characters are corrupted when importing tickets.",
    "WebSocket disconnects after 30 seconds of inactivity.",
    "Admins need a way to view audit history per ticket.",
    "SLA deadlines should trigger reminders 24h before due.",
    "Images over 5MB fail silently on Safari.",
    "Authenticator app setup flow is confusing.",
    "GraphQL would reduce over-fetching on mobile.",
    "Submit button can be double-clicked creating duplicate tickets.",
    "Ctrl+K search shortcut would speed up navigation.",
    "Notification creation creates N+1 queries on ticket update.",
    "Long-polling eats memory after ~2 hours.",
]

COMMENT_BODIES = [
    "Please investigate this issue and provide an update by end of day.",
    "I found the root cause. It's related to the auth middleware configuration.",
    "Deploy after testing is complete. Make sure to run the full test suite first.",
    "Completed. All tests are passing.",
    "Can we prioritize this? It's blocking the release.",
    "I've pushed a fix. Please review the PR.",
    "The issue is reproducible in staging. Here are the steps...",
    "Great work on this! The performance improved by 40%.",
    "Let's schedule a meeting to discuss the approach.",
    "I'll take over this ticket from here.",
    "The client confirmed this is working as expected now.",
    "Added unit tests for the new functionality.",
    "We need to consider edge cases for this feature.",
    "This looks good to merge after the conflict is resolved.",
    "I've documented the API changes in the wiki.",
    "The migration needs to be run before deploying.",
    "Can you add more context to the ticket description?",
    "Fixed the CSS issue on mobile devices.",
    "The integration tests are failing. Investigating now.",
    "This feature is ready for QA testing.",
    "Blocked on this — waiting for the third-party API key.",
    "I've added a retry mechanism to handle transient failures.",
    "We should probably split this into two tickets.",
    "This was actually working before the last deploy.",
    "Verified the fix in the staging environment.",
]

PRIORITIES = [Ticket.Priority.LOW, Ticket.Priority.MEDIUM, Ticket.Priority.HIGH]
STATUSES = [Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS, Ticket.Status.CLOSED]


class Command(BaseCommand):
    help = "Seed the database with users, tickets, comments, notifications, and audit history."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=6)
        parser.add_argument("--tickets", type=int, default=25)
        parser.add_argument("--comments", type=int, default=60)
        parser.add_argument("--password", type=str, default="testpass123")

    def handle(self, *args, **options):
        num_tickets = options["tickets"]
        num_comments = options["comments"]
        password = options["password"]

        self.stdout.write(self.style.NOTICE("Seeding database...\n"))

        admin = self._create_user("admin@example.com", "Admin", "User", User.Role.ADMIN, password, is_staff=True, is_superuser=True)
        manager1 = self._create_user("manager@example.com", "Sarah", "Manager", User.Role.MANAGER, password)
        manager2 = self._create_user("james@example.com", "James", "Hill", User.Role.MANAGER, password)

        agent_specs = [
            ("John", "Agent", "john@example.com"),
            ("Mike", "Developer", "mike@example.com"),
            ("Lisa", "Engineer", "lisa@example.com"),
            ("Tom", "Tester", "tom@example.com"),
            ("Ana", "Designer", "ana@example.com"),
            ("Sam", "Support", "sam@example.com"),
            ("Kate", "Backend", "kate@example.com"),
            ("Raj", "Frontend", "raj@example.com"),
        ]
        agents = [
            self._create_user(email, first, last, User.Role.AGENT, password)
            for first, last, email in agent_specs
        ]

        creators = [admin, manager1, manager2]
        all_users = creators + agents

        # --- Tickets via service layer (triggers notifications + audit) ---
        tickets = []
        assignments_per_ticket = [
            (Ticket.Priority.HIGH, Ticket.Status.OPEN),
            (Ticket.Priority.MEDIUM, Ticket.Status.OPEN),
            (Ticket.Priority.HIGH, Ticket.Status.IN_PROGRESS),
            (Ticket.Priority.LOW, Ticket.Status.CLOSED),
            (Ticket.Priority.MEDIUM, Ticket.Status.IN_PROGRESS),
            (Ticket.Priority.HIGH, Ticket.Status.OPEN),
            (Ticket.Priority.MEDIUM, Ticket.Status.CLOSED),
            (Ticket.Priority.LOW, Ticket.Status.OPEN),
            (Ticket.Priority.HIGH, Ticket.Status.IN_PROGRESS),
            (Ticket.Priority.MEDIUM, Ticket.Status.OPEN),
        ]

        for i in range(num_tickets):
            title = TITLES[i % len(TITLES)]
            desc = DESCRIPTIONS[i % len(DESCRIPTIONS)]
            creator = creators[i % len(creators)]
            priority, status = assignments_per_ticket[i % len(assignments_per_ticket)]
            agent = agents[i % len(agents)]

            ticket = create_ticket(
                title=title,
                description=desc,
                priority=priority,
                status=status,
                created_by=creator,
                assigned_to=agent,
            )
            tickets.append(ticket)

        # --- Simulate status changes (triggers notifications + audit) ---
        for ticket in tickets[:12]:
            old_status = ticket.status
            new_status = random.choice([s for s in STATUSES if s != old_status])
            updater = random.choice(creators)
            update_ticket(ticket, changed_by=updater, status=new_status)

        # --- Simulate priority changes ---
        for ticket in tickets[8:18]:
            old_priority = ticket.priority
            new_priority = random.choice([p for p in PRIORITIES if p != old_priority])
            updater = random.choice(creators)
            update_ticket(ticket, changed_by=updater, priority=new_priority)

        # --- Simulate reassignment (triggers notifications + audit) ---
        for ticket in tickets[5:15]:
            new_assignee = random.choice(agents)
            changer = random.choice(creators)
            assign_ticket(ticket, new_assignee, changed_by=changer)

        # --- Comments via service layer (triggers notifications) ---
        for _i in range(num_comments):
            ticket = random.choice(tickets)
            author = random.choice(all_users)
            body = random.choice(COMMENT_BODIES)
            create_comment(ticket=ticket, author=author, body=body)

        # --- Mark ~30% of notifications as read so users can test the badge ---
        from apps.notifications.models import Notification

        all_notifs = list(Notification.objects.all())
        read_count = int(len(all_notifs) * 0.3)
        for n in all_notifs[:read_count]:
            n.is_read = True
            n.save(update_fields=["is_read"])

        # --- Summary ---
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
        self.stdout.write(self.style.SUCCESS(f"  Users:         {User.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Tickets:       {Ticket.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Comments:      {Comment.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Notifications: {Notification.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("\nLogin credentials:"))
        self.stdout.write(self.style.SUCCESS(f"  Admin:    admin@example.com / {password}"))
        self.stdout.write(self.style.SUCCESS(f"  Manager:  manager@example.com / {password}"))
        self.stdout.write(self.style.SUCCESS(f"  Agent:    john@example.com / {password}"))

    def _create_user(self, email, first, last, role, password, **extra):
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first,
                "last_name": last,
                "role": role,
                "is_active": True,
                **extra,
            },
        )
        user.set_password(password)
        user.save()
        self.stdout.write(f"  User: {email} ({role})")
        return user
