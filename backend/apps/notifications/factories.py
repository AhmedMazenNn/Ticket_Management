import factory

from apps.accounts.factories import UserFactory
from apps.tickets.factories import TicketFactory

from .models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    ticket = factory.SubFactory(TicketFactory)
    user = factory.SubFactory(UserFactory)
    type = Notification.Type.TICKET_ASSIGNED
    is_read = False
