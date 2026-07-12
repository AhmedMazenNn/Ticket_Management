import factory

from apps.accounts.factories import UserFactory
from apps.tickets.factories import TicketFactory

from .models import TicketHistory


class TicketHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TicketHistory

    ticket = factory.SubFactory(TicketFactory)
    changed_by = factory.SubFactory(UserFactory)
    field_name = "status"
    old_value = "Open"
    new_value = "In Progress"
