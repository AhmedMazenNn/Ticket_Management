import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.comments.models import Comment
from apps.tickets.models import Ticket

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample users, tickets, and comments."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=6, help="Number of non-admin users to create (default: 6)"
        )
        parser.add_argument(
            "--tickets", type=int, default=15, help="Number of tickets to create (default: 15)"
        )
        parser.add_argument(
            "--comments", type=int, default=40, help="Number of comments to create (default: 40)"
        )
        parser.add_argument(
            "--password",
            type=str,
            default="testpass123",
            help="Password for all created users (default: testpass123)",
        )

    def handle(self, *args, **options):
        num_users = options["users"]
        num_tickets = options["tickets"]
        num_comments = options["comments"]
        password = options["password"]

        self.stdout.write(self.style.NOTICE("Seeding database..."))

        # --- Users ---
        admin, _ = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin.set_password(password)
        admin.save()
        self.stdout.write(f"  Admin: admin@example.com / {password}")

        manager, _ = User.objects.get_or_create(
            email="manager@example.com",
            defaults={
                "first_name": "Sarah",
                "last_name": "Manager",
                "role": User.Role.MANAGER,
                "is_active": True,
            },
        )
        manager.set_password(password)
        manager.save()
        self.stdout.write(f"  Manager: manager@example.com / {password}")

        agents = []
        agent_data = [
            ("John", "Agent", "john@example.com"),
            ("Mike", "Developer", "mike@example.com"),
            ("Lisa", "Engineer", "lisa@example.com"),
            ("Tom", "Tester", "tom@example.com"),
            ("Ana", "Designer", "ana@example.com"),
            ("Sam", "Support", "sam@example.com"),
        ]
        for first, last, email in agent_data[:num_users]:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": User.Role.AGENT,
                    "is_active": True,
                },
            )
            user.set_password(password)
            user.save()
            agents.append(user)
            self.stdout.write(f"  Agent: {email} / {password}")

        all_users = [admin, manager] + agents
        creators = [admin, manager]
        assignees = agents if agents else [admin, manager]

        # --- Tickets ---
        ticket_data = [
            ("Fix login page redirect bug", "Users are redirected to a 404 page after successful login on Chrome.", "HIGH", "OPEN"),
            ("Update API documentation", "The Swagger docs need to be updated with the new comments endpoints.", "MEDIUM", "IN_PROGRESS"),
            ("Database migration review", "Review the latest migration files before deploying to production.", "HIGH", "OPEN"),
            ("Add email notifications", "Send email when a ticket is assigned to an agent.", "MEDIUM", "OPEN"),
            ("Fix dashboard chart rendering", "Doughnut chart shows blank on Safari browsers.", "LOW", "CLOSED"),
            ("Optimize ticket list query", "The ticket list endpoint is slow with 10k+ records.", "HIGH", "IN_PROGRESS"),
            ("Add ticket export to CSV", "Managers need to export ticket data for reporting.", "MEDIUM", "OPEN"),
            ("Fix pagination on mobile", "Page numbers overlap on small screens.", "LOW", "CLOSED"),
            ("Implement comment editing", "Users should be able to edit their own comments.", "MEDIUM", "CLOSED"),
            ("Add role-based filtering", "Allow filtering tickets by assignee role.", "LOW", "OPEN"),
            ("Fix timezone display", "Timestamps show UTC instead of user's local timezone.", "MEDIUM", "IN_PROGRESS"),
            ("Add ticket priority sorting", "Allow sorting tickets by priority in the list view.", "LOW", "OPEN"),
            ("Review security headers", "Ensure all security headers are properly configured.", "HIGH", "OPEN"),
            ("Add dark mode support", "Implement a dark mode toggle in the settings page.", "LOW", "OPEN"),
            ("Fix CSV import encoding", "UTF-8 characters are corrupted when importing tickets.", "MEDIUM", "CLOSED"),
        ]

        tickets = []
        for _i, (title, desc, priority, status) in enumerate(ticket_data[:num_tickets]):
            creator = random.choice(creators)
            assignee = random.choice(assignees) if random.random() > 0.2 else None
            ticket = Ticket.objects.create(
                title=title,
                description=desc,
                priority=priority,
                status=status,
                created_by=creator,
                assigned_to=assignee,
            )
            tickets.append(ticket)
        self.stdout.write(f"  Created {len(tickets)} tickets")

        # --- Comments ---
        comment_bodies = [
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
        ]

        created_comments = []
        for _i in range(num_comments):
            ticket = random.choice(tickets)
            author = random.choice(all_users)
            body = random.choice(comment_bodies)
            comment = Comment.objects.create(
                ticket=ticket,
                author=author,
                body=body,
            )
            created_comments.append(comment)
        self.stdout.write(f"  Created {len(created_comments)} comments")

        self.stdout.write(self.style.SUCCESS("\nSeeding complete!"))
        self.stdout.write(self.style.SUCCESS(f"  Users:  {User.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Tickets: {Ticket.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"  Comments: {Comment.objects.count()}"))
        self.stdout.write(self.style.SUCCESS(f"\nAdmin login: admin@example.com / {password}"))
