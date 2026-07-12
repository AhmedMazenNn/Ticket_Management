import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = User.Role.AGENT
    is_active = True

    @factory.post_generation
    def password(self, create: bool, extracted: str | None, **kwargs: dict) -> None:
        password = extracted or "testpass123"
        self.set_password(password)
        if create:
            self.save()


class AdminUserFactory(UserFactory):
    role = User.Role.ADMIN
    is_staff = True
    is_superuser = True
