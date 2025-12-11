from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField

User = get_user_model()

class Teacher(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    first_name = models.CharField(
        verbose_name="Имя",
        help_text="Имя учителя",
        max_length=127
    )
    second_name = models.CharField(
        verbose_name="Фамилия"
    )
    bio = models.TextField(
        verbose_name="Описание",
        help_text="Описание учителя себя"
    )
    avatar = models.ImageField(
        _("Аватар"),
        upload_to="users/avatars/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"


class Course(models.Model):
    """
    Базовый объект образовательной платформы. Каждый курс принадлежит конкретному
    инструктору (кастомная модель пользователя) и содержит краткое/полное описание.
    """
    class Level(models.TextChoices):
        BEGINNER = "beginner", _("Начальный")
        INTERMEDIATE = "intermediate", _("Средний")
        ADVANCED = "advanced", _("Продвинутый")

    teacher = models.ForeignKey(
        Teacher,
        verbose_name=_("Автор курса"),
        related_name="courses",
        on_delete=models.CASCADE,
    )
    level = models.CharField(
        _("Уровень сложности"), choices=Level.choices, default=Level.BEGINNER, max_length=20
    )
    title = models.CharField(_("Название курса"), max_length=200)
    description = models.TextField(_("Подробное описание"))
    short_description = models.TextField(_("Краткий питч"), max_length=500, blank=True)
    preview_image = models.ImageField(
        _("Обложка"), upload_to="courses/previews/", blank=True, null=True
    )
    duration_hours = models.PositiveIntegerField(_("Продолжительность (часы)"), default=1)
    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField(_("Бесплатный курс"), default=False)
    is_published = models.BooleanField(_("Опубликован"), default=False)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлён"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """
    Урок внутри курса. Lesson связан по FK и хранит контент, ссылку на видео и длительность.
    """
    course = models.ForeignKey(
        Course,
        verbose_name=_("Курс"),
        related_name="lessons",
        on_delete=models.CASCADE,
    )
    title = models.CharField(_("Название урока"), max_length=200)
    content = HTMLField(_("Контент"))
    video_url = models.URLField(_("Видео"), blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(_("Продолжительность (мин)"), default=1)
    order = models.PositiveIntegerField(_("Порядок"), default=0)
    is_published = models.BooleanField(_("Опубликован"), default=False)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлён"), auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = ("course", "order")
        verbose_name = _("Урок")
        verbose_name_plural = _("Уроки")

    def __str__(self):
        return f"{self.course.title} · {self.title}"
