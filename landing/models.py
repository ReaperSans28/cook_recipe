from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=63)


class Lesson(models.Model):
    name = models.CharField(max_length=63)
