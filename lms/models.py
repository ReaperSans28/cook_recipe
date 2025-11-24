from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    """
    Базовый объект образовательной платформы. Каждый курс принадлежит конкретному
    инструктору (кастомная модель пользователя) и содержит краткое/полное описание.
    """

    class Level(models.TextChoices):
        BEGINNER = "beginner", _("Начальный")
        INTERMEDIATE = "intermediate", _("Средний")
        ADVANCED = "advanced", _("Продвинутый")

    title = models.CharField(_("Название курса"), max_length=200)
    description = models.TextField(_("Подробное описание"))
    short_description = models.TextField(_("Краткий питч"), max_length=500, blank=True)
    preview_image = models.ImageField(
        _("Обложка"), upload_to="courses/previews/", blank=True, null=True
    )
    level = models.CharField(
        _("Уровень сложности"), choices=Level.choices, default=Level.BEGINNER, max_length=20
    )
    duration_hours = models.PositiveIntegerField(_("Продолжительность (часы)"), default=1)
    price = models.DecimalField(_("Цена"), max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField(_("Бесплатный курс"), default=False)
    is_published = models.BooleanField(_("Опубликован"), default=False)
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Обновлён"), auto_now=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Автор курса"),
        related_name="courses",
        on_delete=models.CASCADE,
    )

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
    content = models.TextField(_("Контент"))
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
