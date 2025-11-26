from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Создаёт суперпользователя без интерактивных вопросов. Удобно для CI/CD."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Имя пользователя")
        parser.add_argument("--email", required=True, help="Email пользователя")
        parser.add_argument("--password", required=True, help="Пароль")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        if User.objects.filter(username=username).exists():
            raise CommandError(f"Пользователь {username} уже существует")

        User.objects.create_superuser(
            username=username,
            email=options["email"],
            password=options["password"],
            is_instructor=True,
        )
        self.stdout.write(self.style.SUCCESS("Суперпользователь создан"))


