import factory

from apps.accounts.factories import UserFactory
from apps.tickets.factories import TicketFactory

from .models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    ticket = factory.SubFactory(TicketFactory)
    author = factory.SubFactory(UserFactory)
    body = factory.Faker("sentence")
