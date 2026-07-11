import factory

from apps.accounts.factories import UserFactory

from .models import Ticket


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket

    title = factory.Sequence(lambda n: f"Ticket {n}")
    description = factory.Faker("sentence")
    priority = Ticket.Priority.MEDIUM
    status = Ticket.Status.OPEN
    assigned_to = factory.SubFactory(UserFactory)
    created_by = factory.SubFactory(UserFactory)
