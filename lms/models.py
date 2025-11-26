from django.db import models
from django.db.models import ForeignKey
from rest_framework.fields import SlugField, IntegerField
from tinymce.models import HTMLField
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser

# Все поля можно найти в fields. Для этого зажав ctrl нажмите на fields в ссылке: django.db.models.fields
class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(verbose_name="Название")
    slug = SlugField(max_length=255)
    short_description = models.CharField(max_length=255, verbose_name="Краткое описание")
    full_description = HTMLField(verbose_name="Полное описание")
    price = models.PositiveIntegerField(verbose_name="Цена")
    avatar = models.ImageField(verbose_name="Аватар курса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    publish = models.BooleanField(verbose_name="Опубликован ли", default=False)
    author = ForeignKey(
        AbstractUser,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


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


class TrafficCourse(models.Model):
    user = models.ForeignKey(
        AbstractUser,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Трафик курса")
        verbose_name_plural = _("Траффики курсов")
