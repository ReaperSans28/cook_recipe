from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт обычного пользователя/студента с заданным паролем."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo_student", help="Имя пользователя")
        parser.add_argument("--email", default="student@example.com", help="Email пользователя")
        parser.add_argument("--password", default="student123", help="Пароль")
        parser.add_argument(
            "--instructor",
            action="store_true",
            help="Добавить флаг инструктора. По умолчанию создаётся студент.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        email = options["email"]
        password = options["password"]
        is_instructor = options["instructor"]

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_instructor": is_instructor,
            },
        )
        if not created:
            self.stdout.write(self.style.WARNING("Пользователь уже существует — обновляю пароль"))

        user.set_password(password)
        user.save(update_fields=["password"])
        self.stdout.write(self.style.SUCCESS(f"Пользователь {user.username} готов"))


