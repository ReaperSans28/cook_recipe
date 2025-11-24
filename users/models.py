from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя. Добавляем флаг преподавателя и небольшую анкету.
    """

    headline = models.CharField("Короткий заголовок", max_length=120, blank=True)
    bio = models.TextField("О себе", blank=True)
    is_instructor = models.BooleanField("Может создавать курсы", default=False)
    avatar = models.ImageField("Аватар", upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.get_full_name() or self.username
