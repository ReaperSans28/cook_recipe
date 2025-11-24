# from django.db import models
# from django.db.models import ForeignKey
# from rest_framework.fields import SlugField, IntegerField
# from tinymce.models import HTMLField
#
# from users.models import CustomUser
#
# # Все поля можно найти в fields. Для этого зажав ctrl нажмите на fields в ссылке: django.db.models.fields
# class Course(models.Model):
#     class Status(models.TextChoices):
#         DRAFT = 'DF', 'Draft'
#         PUBLISHED = 'PB', 'Published'
#
#     title = models.CharField(verbose_name="Название")
#     slug = SlugField(max_length=255)
#     short_description = models.CharField(max_length=255, verbose_name="Краткое описание")
#     full_description = HTMLField(verbose_name="Полное описание")
#     price = models.PositiveIntegerField(verbose_name="Цена")
#     avatar = models.ImageField(verbose_name="Аватар курса")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
#     updated_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=2,
#                               choices=Status.choices,
#                               default=Status.DRAFT)
#     publish = models.BooleanField(verbose_name="Опубликован ли", default=False)
#     author = ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         verbose_name="Автор"
#     )
